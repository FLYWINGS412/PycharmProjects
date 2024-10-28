import os
import json
import time
import threading
import subprocess
import tkinter as tk
from threading import Lock
from tkinter.scrolledtext import ScrolledText

# 设备运行状态管理（存储设备与其对应的进程）
device_processes = {}
log_data = {}  # 存储设备的日志数据
log_buttons = {}  # 存储日志按钮
current_log_display = None  # 当前显示的日志
log_lock = Lock()  # 日志更新锁

# 读取 config.json 配置文件
with open('config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 创建 GUI
root = tk.Tk()
root.title("设备管理")

# 获取屏幕尺寸
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# 设置左侧设备区域的最大和最小高度
MAX_HEIGHT = int(screen_height * 0.8)
MIN_HEIGHT = 400  # 设置最小高度

# 创建左侧容器框架
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

# 初始化鼠标滚轮的滑动行为
def on_mouse_wheel(event):
    if event.delta < 0 and device_canvas.yview()[1] < 1.0:
        device_canvas.yview_scroll(1, "unit")
    elif event.delta > 0 and device_canvas.yview()[0] > 0.0:
        device_canvas.yview_scroll(-1, "unit")

device_canvas.bind_all("<MouseWheel>", on_mouse_wheel)

# 调整左侧容器框架的高度和 Canvas 滚动区域
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

# 为每个设备创建按钮和日志按钮
device_buttons = {}
log_buttons = {}
for device_name in config.keys():
    frame = tk.Frame(device_frame)
    frame.pack(fill=tk.X, pady=1)

    device_button = tk.Button(frame, text=device_name, width=12)
    device_button.pack(side=tk.LEFT, padx=3)

    log_button = tk.Button(frame, text="日志", width=5)
    log_button.pack(side=tk.RIGHT, padx=3)

    log_data[device_name] = ""

    def make_toggle_device(name):
        return lambda btn=device_button: toggle_device(name, btn)

    def make_show_log(name):
        return lambda: show_or_hide_log(name)

    device_button.config(command=make_toggle_device(device_name))
    log_button.config(command=make_show_log(device_name))

    device_buttons[device_name] = device_button
    log_buttons[device_name] = log_button

# 创建右侧显示区域，包含日志标签和日志显示框
right_frame = tk.Frame(root)
log_tab_frame = tk.Frame(right_frame)
log_display_frame = tk.Frame(right_frame)
log_text = ScrolledText(log_display_frame, wrap=tk.WORD)
log_text.pack(fill=tk.BOTH, expand=True)

# 启动设备
def start_device(device_name, button):
    device_info = config.get(device_name)

    if not device_info:
        raise ValueError(f"Device '{device_name}' not found in config.json")

    # 动态生成配置
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

    # 获取当前脚本目录，确保调用的是 main.py 而不是重新调用 tj.py
    current_dir = os.path.dirname(os.path.abspath(__file__))
    main_script_path = os.path.join(current_dir, 'main.py')

    # 传递 `desired_caps` 作为 JSON 字符串
    process = subprocess.Popen(
        ['python', main_script_path, json.dumps(desired_caps)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8',
        creationflags=subprocess.CREATE_NO_WINDOW  # 隐藏终端窗口
    )

    # 将设备和进程映射存储
    device_processes[device_name] = process

    # 初始化日志数据
    log_data[device_name] = ""

    # 改变按钮颜色为绿色，表示设备启动
    button.config(bg='green', text=device_name)

    # 启动日志更新线程
    threading.Thread(target=update_log, args=(device_name, process), daemon=True).start()

def update_log(device_name, process):
    while process.poll() is None:
        output = process.stdout.readline()
        if output:
            with log_lock:
                log_data[device_name] += output
                if current_log_display == device_name:
                    root.after(0, lambda: update_log_text(device_name))
        time.sleep(0.1)

def update_log_text(device_name):
    log_text.delete(1.0, tk.END)
    log_text.insert(tk.END, log_data[device_name])
    log_text.see(tk.END)

# 停止设备
def stop_device(device_name, button):
    if device_name in device_processes:
        process = device_processes[device_name]
        if process.poll() is None:
            process.terminate()
            print(f"停止设备 {device_name} 的自动化任务...")
        del device_processes[device_name]
        button.config(bg='SystemButtonFace', text=device_name)

# 切换设备状态
def toggle_device(device_name, button):
    if device_name in device_processes:
        stop_device(device_name, button)
    else:
        start_device(device_name, button)

# 显示或隐藏日志标签和内容
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

root.update_idletasks()
x = 10
y = int((screen_height - root.winfo_height()) / 2)
root.geometry(f"+{x}+{y}")
root.mainloop()