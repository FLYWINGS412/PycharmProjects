import json
import subprocess
import tkinter as tk
from tkinter.scrolledtext import ScrolledText
import threading
import time

# 设备运行状态管理（存储设备与其对应的进程）
device_processes = {}
log_texts = {}  # 存储每个设备的日志内容
log_windows = {}  # 存储每个设备的日志窗口
log_data = {}  # 存储设备的日志数据

# 读取 config.json 配置文件
with open('config.json', 'r') as f:
    config = json.load(f)

# 启动设备
def start_device(device_name, button):
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

    # 初始化日志数据
    log_data[device_name] = ""

    # 改变按钮颜色为绿色，表示设备启动，并显示设备名
    button.config(bg='green', text=f'{device_name} (运行中)')

    # 实时更新日志
    def update_log():
        while process.poll() is None:
            output = process.stdout.readline()
            if output:
                log_data[device_name] += output  # 保存日志数据
                if device_name in log_texts and log_texts[device_name].winfo_exists():
                    log_texts[device_name].insert(tk.END, output)
                    log_texts[device_name].see(tk.END)
            time.sleep(0.1)  # 每100ms检查一次日志输出

    # 启动日志更新线程
    threading.Thread(target=update_log, daemon=True).start()

# 停止设备
def stop_device(device_name, button):
    if device_name in device_processes:
        process = device_processes[device_name]
        if process.poll() is None:  # 进程仍在运行
            process.terminate()
            print(f"Stopping device {device_name}...")
        del device_processes[device_name]

        # 改变按钮颜色为灰色，表示设备已停止，并显示设备名
        button.config(bg='SystemButtonFace', text=device_name)

    # 销毁日志窗口
    if device_name in log_windows:
        log_windows[device_name].destroy()
        del log_windows[device_name]
        del log_texts[device_name]

# 点击设备按钮时的行为
def toggle_device(device_name, button):
    if device_name in device_processes:
        stop_device(device_name, button)
    else:
        start_device(device_name, button)

# 点击日志按钮时显示日志窗口
def show_log(device_name):
    if device_name not in log_windows or not log_windows[device_name].winfo_exists():
        # 如果日志窗口不存在或者已经被销毁，重新创建
        log_window = tk.Toplevel()
        log_window.title(f"{device_name} 日志")

        # 创建一个文本框来显示日志
        log_text = ScrolledText(log_window, height=20, wrap=tk.WORD)
        log_text.pack(fill=tk.BOTH, expand=True)

        # 如果有之前的日志数据，填充到日志框
        if device_name in log_data:
            log_text.insert(tk.END, log_data[device_name])

        # 将日志框和日志窗口存储起来
        log_texts[device_name] = log_text
        log_windows[device_name] = log_window
    else:
        # 如果日志窗口已经存在，激活它
        log_windows[device_name].deiconify()

# 创建 GUI
root = tk.Tk()
root.title("设备管理")

# 创建设备列表区域带滚动条
device_frame = tk.Frame(root)
device_canvas = tk.Canvas(device_frame)
device_scrollbar = tk.Scrollbar(device_frame, orient="vertical", command=device_canvas.yview)
scrollable_frame = tk.Frame(device_canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: device_canvas.configure(
        scrollregion=device_canvas.bbox("all")
    )
)

device_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
device_canvas.configure(yscrollcommand=device_scrollbar.set)

device_frame.pack(side=tk.LEFT, fill=tk.Y)
device_canvas.pack(side=tk.LEFT, fill=tk.Y, expand=True)
device_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# 为每个设备创建按钮和日志按钮
device_buttons = {}
for device_name in config.keys():
    # 使用 device_name 显示按钮名（例如 device_1, device_2）
    frame = tk.Frame(scrollable_frame)
    frame.pack(fill=tk.X, pady=5)

    device_button = tk.Button(frame, text=device_name, width=15)
    device_button.pack(side=tk.LEFT)

    # 创建日志按钮
    log_button = tk.Button(frame, text="日志", width=10)
    log_button.pack(side=tk.RIGHT)

    # 设备按钮点击事件
    device_button.config(command=lambda name=device_name, btn=device_button: toggle_device(name, btn))

    # 日志按钮点击事件
    log_button.config(command=lambda name=device_name: show_log(name))

    device_buttons[device_name] = device_button

root.mainloop()
