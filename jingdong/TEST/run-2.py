import json
import subprocess
import tkinter as tk
from tkinter import ttk
from tkinter.scrolledtext import ScrolledText
import os
import threading
import time

# 设备运行状态管理（存储设备与其对应的进程）
device_processes = {}

# 读取 config.json 配置文件
with open('config.json', 'r') as f:
    config = json.load(f)

# 启动设备
def start_device(device_name, log_tab, log_text, button, display_name):
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

    # 启动设备的自动化任务
    print(f"Starting device {device_name}...")

    # 设置编码为 'utf-8'，避免 gbk 编码问题
    process = subprocess.Popen(['python', 'main.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')

    # 将设备和进程映射存储
    device_processes[device_name] = process

    # 改变按钮颜色为绿色，表示设备启动，并显示设备名
    button.config(bg='green', text=f'{display_name} (运行中)')

    # 实时更新日志
    def update_log():
        while process.poll() is None:
            output = process.stdout.readline()
            if output:
                log_text.insert(tk.END, output)
                log_text.see(tk.END)
            time.sleep(0.1)  # 每100ms检查一次日志输出

    threading.Thread(target=update_log, daemon=True).start()

# 停止设备
def stop_device(device_name, button, display_name):
    if device_name in device_processes:
        process = device_processes[device_name]
        if process.poll() is None:  # 进程仍在运行
            process.terminate()
            print(f"Stopping device {device_name}...")
        del device_processes[device_name]

        # 改变按钮颜色为灰色，表示设备已停止，并显示设备名
        button.config(bg='SystemButtonFace', text=display_name)

# 点击设备按钮时的行为
def toggle_device(device_name, log_tab, log_text, button, display_name):
    if device_name in device_processes:
        stop_device(device_name, button, display_name)
    else:
        start_device(device_name, log_tab, log_text, button, display_name)

# 创建 GUI
root = tk.Tk()
root.title("设备管理")

# 创建设备列表区域
device_frame = tk.Frame(root)
device_frame.pack(side=tk.LEFT, fill=tk.Y)

# 创建日志区域
log_frame = tk.Frame(root)
log_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# 创建日志标签页
notebook = ttk.Notebook(log_frame)
notebook.pack(fill=tk.BOTH, expand=True)

# 为每个设备创建按钮
device_buttons = {}
for device_name in config.keys():
    device_info = config[device_name]
    display_name = device_info['deviceName']  # 使用设备的 deviceName 字段作为按钮文本

    device_button = tk.Button(device_frame, text=display_name, width=20)
    device_button.pack(pady=5)
    device_buttons[device_name] = device_button

    # 每个按钮的点击行为
    device_button.config(command=lambda name=device_name, btn=device_button, display=display_name: on_device_click(name, btn, display))

# 点击设备时的行为
def on_device_click(device_name, button, display_name):
    if device_name in device_processes:
        toggle_device(device_name, None, None, button, display_name)  # 停止设备
    else:
        # 新建日志标签
        log_tab = ttk.Frame(notebook)
        notebook.add(log_tab, text=f"{display_name} 日志")

        # 添加日志显示框
        log_text = ScrolledText(log_tab, wrap=tk.WORD, height=10)
        log_text.pack(fill=tk.BOTH, expand=True)

        # 启动设备
        toggle_device(device_name, log_tab, log_text, button, display_name)

root.mainloop()
