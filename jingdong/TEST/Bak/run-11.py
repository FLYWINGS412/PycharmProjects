import os
import sys
import json
import time
import threading
import subprocess
import tkinter as tk
from threading import Lock
from tkinter.scrolledtext import ScrolledText

# 设备运行状态管理（存储设备与其对应的进程）
device_processes = {}  # 存储设备名和对应进程的字典
log_data = {}  # 存储每个设备日志内容
log_buttons = {}  # 存储日志按钮
current_log_display = None  # 当前显示的日志设备名
log_lock = Lock()  # 用于线程安全地更新日志数据

# 获取当前目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 读取 config.json 配置文件
config_path = os.path.join(current_dir, 'config.json')
with open(config_path, 'r', encoding='utf-8') as f:
    config = json.load(f)

# 创建 GUI 主窗口
root = tk.Tk()
root.title("设备管理")

# 获取屏幕尺寸
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# 设置左侧设备区域的最大和最小高度
MAX_HEIGHT = int(screen_height * 0.8)  # 最大高度为屏幕高度的80%
MIN_HEIGHT = 400  # 设置最小高度

# 创建左侧设备列表区域的框架
left_frame = tk.Frame(root)
left_frame.pack(side=tk.LEFT, anchor='nw')

# 创建 Canvas 和 Scrollbar
device_canvas = tk.Canvas(left_frame, width=200)
device_scrollbar = tk.Scrollbar(left_frame, orient="vertical", command=device_canvas.yview)
device_canvas.configure(yscrollcommand=device_scrollbar.set)

device_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
device_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# 创建设备列表框架，放置在 Canvas 中
device_frame = tk.Frame(device_canvas)
device_canvas.create_window((0, 0), window=device_frame, anchor='nw')

# 鼠标滚轮控制设备区域滚动
def on_mouse_wheel(event):
    if event.delta < 0 and device_canvas.yview()[1] < 1.0:
        device_canvas.yview_scroll(1, "unit")
    elif event.delta > 0 and device_canvas.yview()[0] > 0.0:
        device_canvas.yview_scroll(-1, "unit")

device_canvas.bind_all("<MouseWheel>", on_mouse_wheel)

# 调整左侧设备区域的高度和滚动区域
def adjust_left_frame_height(event=None):
    device_frame.update_idletasks()
    total_height = device_frame.winfo_height()
    total_width = device_frame.winfo_width()

    height = min(max(total_height, MIN_HEIGHT), MAX_HEIGHT)
    left_frame.config(height=height, width=total_width + device_scrollbar.winfo_width())
    left_frame.pack_propagate(False)

    if device_canvas.bbox("all"):
        device_canvas.config(scrollregion=device_canvas.bbox("all"), height=height)

device_frame.bind("<Configure>", adjust_left_frame_height)

# 为每个设备创建对应的启动按钮和日志按钮
device_buttons = {}  # 存储设备按钮
log_buttons = {}  # 存储日志按钮
for device_name in config.keys():
    # 创建每个设备的框架
    frame = tk.Frame(device_frame)
    frame.pack(fill=tk.X, pady=1)

    # 创建设备按钮
    device_button = tk.Button(frame, text=device_name, width=12)
    device_button.pack(side=tk.LEFT, padx=3)

    # 创建日志按钮
    log_button = tk.Button(frame, text="日志", width=5)
    log_button.pack(side=tk.RIGHT, padx=3)

    log_data[device_name] = ""  # 初始化每个设备的日志内容为空

    # 创建按钮点击事件的闭包函数
    def make_toggle_device(name):
        return lambda btn=device_button: toggle_device(name, btn)

    def make_show_log(name):
        return lambda: show_or_hide_log(name)

    # 将点击事件绑定到按钮
    device_button.config(command=make_toggle_device(device_name))
    log_button.config(command=make_show_log(device_name))

    device_buttons[device_name] = device_button  # 存储设备按钮
    log_buttons[device_name] = log_button  # 存储日志按钮

# 创建右侧显示区域，用于显示日志内容
right_frame = tk.Frame(root)
log_tab_frame = tk.Frame(right_frame)
log_display_frame = tk.Frame(right_frame)

# 日志显示框
log_text = ScrolledText(log_display_frame, wrap=tk.WORD)
log_text.pack(fill=tk.BOTH, expand=True)

# 启动设备的自动化任务
def start_device(device_name, button):
    device_info = config.get(device_name)
    if not device_info:
        print(f"设备 '{device_name}' 未找到配置。")
        return

    # 设备的自动化配置
    desired_caps = {
        'platformName': 'Android',
        'platformVersion': '9',
        'deviceName': device_info['deviceName'],
        'udid': device_info['udid'],
        'automationName': 'UiAutomator2',
        'settings[waitForIdleTimeout]': 10,
        'settings[waitForSelectorTimeout]': 10,
        'newCommandTimeout': 21600,
        'ignoreHiddenApiPolicyError': True,
        'dontStopAppOnReset': True,
        'noReset': True,
    }

    print(f"启动设备 {device_name} 的自动化任务...")

    main_path = os.path.join(current_dir, 'main.py')  # 获取 main.py 的路径
    process = subprocess.Popen(
        [sys.executable, main_path, json.dumps(desired_caps)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8'
    )

    device_processes[device_name] = process  # 存储设备对应的进程
    log_data[device_name] = ""  # 初始化日志内容
    button.config(bg='green', text=device_name)  # 将按钮背景色设置为绿色

    threading.Thread(target=update_log, args=(device_name, process), daemon=True).start()  # 开始日志更新线程

# 实时更新日志
def update_log(device_name, process):
    while process.poll() is None:
        output = process.stdout.readline()
        if output:
            with log_lock:
                log_data[device_name] += output
                if current_log_display == device_name:
                    root.after(0, lambda: update_log_text(device_name))  # 更新 Tkinter UI
        time.sleep(0.1)

# 将最新的日志内容显示在日志框中
def update_log_text(device_name):
    log_text.delete(1.0, tk.END)
    log_text.insert(tk.END, log_data[device_name])
    log_text.see(tk.END)

# 停止设备的自动化任务
def stop_device(device_name, button):
    if device_name in device_processes:
        process = device_processes[device_name]
        if process.poll() is None:
            process.terminate()
            print(f"停止设备 {device_name} 的自动化任务...")
        del device_processes[device_name]  # 删除设备进程记录
        button.config(bg='SystemButtonFace', text=device_name)  # 将按钮背景色恢复

# 切换设备的启动/停止状态
def toggle_device(device_name, button):
    if device_name in device_processes:
        stop_device(device_name, button)
    else:
        start_device(device_name, button)

# 显示或隐藏设备的日志
def show_or_hide_log(device_name):
    global current_log_display
    if device_name not in log_data:
        log_data[device_name] = ""

    if current_log_display == device_name:
        log_buttons[device_name].config(bg='SystemButtonFace', text='日志')
        log_tab_frame.pack_forget()
        log_display_frame.pack_forget()
        right_frame.pack_forget()
        current_log_display = None
    else:
        if current_log_display:
            log_buttons[current_log_display].config(bg='SystemButtonFace', text='日志')
        log_buttons[device_name].config(bg='green', text='日志')
        log_text.delete(1.0, tk.END)
        log_text.insert(tk.END, log_data[device_name])
        log_text.see(tk.END)
        current_log_display = device_name
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        log_tab_frame.pack(side=tk.TOP, fill=tk.X)
        log_display_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

# 窗口布局设置
root.update_idletasks()
x = 10
y = int((screen_height - root.winfo_height()) / 2)
root.geometry(f"+{x}+{y}")
root.mainloop()
