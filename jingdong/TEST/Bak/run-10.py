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
device_canvas = tk.Canvas(left_frame, width=200)  # 增加 Canvas 宽度，确保滚动条和按钮之间有足够间隔
device_scrollbar = tk.Scrollbar(left_frame, orient="vertical", command=device_canvas.yview)
device_canvas.configure(yscrollcommand=device_scrollbar.set)

device_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
device_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# 创建设备列表框架，放置在 Canvas 中
device_frame = tk.Frame(device_canvas)
device_canvas.create_window((0, 0), window=device_frame, anchor='nw')

# 初始化鼠标滚轮的滑动行为
def on_mouse_wheel(event):
    # 如果向下滚动，且未到底部
    if event.delta < 0 and device_canvas.yview()[1] < 1.0:
        device_canvas.yview_scroll(1, "unit")
    # 如果向上滚动，且未到顶部
    elif event.delta > 0 and device_canvas.yview()[0] > 0.0:
        device_canvas.yview_scroll(-1, "unit")

# 绑定鼠标滚轮事件
device_canvas.bind_all("<MouseWheel>", on_mouse_wheel)

# 调整左侧容器框架的高度和 Canvas 滚动区域
def adjust_left_frame_height(event=None):
    device_frame.update_idletasks()
    total_height = device_frame.winfo_height()
    total_width = device_frame.winfo_width()

    height = min(max(total_height, MIN_HEIGHT), MAX_HEIGHT)
    left_frame.config(height=height, width=total_width + device_scrollbar.winfo_width())
    left_frame.pack_propagate(False)

    # 避免重新初始化时发生跳动
    if device_canvas.bbox("all"):
        device_canvas.config(scrollregion=device_canvas.bbox("all"), height=height)

# 绑定设备框架大小变化事件
device_frame.bind("<Configure>", adjust_left_frame_height)

# 为每个设备创建按钮和日志按钮
device_buttons = {}
log_buttons = {}  # 创建存储日志按钮的字典
for device_name in config.keys():
    frame = tk.Frame(device_frame)
    frame.pack(fill=tk.X, pady=1)

    device_button = tk.Button(frame, text=device_name, width=12)
    device_button.pack(side=tk.LEFT, padx=3)

    log_button = tk.Button(frame, text="日志", width=5)
    log_button.pack(side=tk.RIGHT, padx=3)

    # 初始化每个设备的日志数据为空字符串
    log_data[device_name] = ""  # 确保每个设备都有对应的日志数据

    # 使用闭包确保每个按钮传递正确的 device_name
    def make_toggle_device(name):
        return lambda btn=device_button: toggle_device(name, btn)

    def make_show_log(name):
        return lambda: show_or_hide_log(name)

    # 为按钮配置命令
    device_button.config(command=make_toggle_device(device_name))
    log_button.config(command=make_show_log(device_name))

    # 将设备按钮和日志按钮分别存储在字典中
    device_buttons[device_name] = device_button
    log_buttons[device_name] = log_button  # 存储日志按钮

# 创建右侧显示区域，包含日志标签和日志显示框
right_frame = tk.Frame(root)

# 日志标签框，初始状态隐藏
log_tab_frame = tk.Frame(right_frame)
log_display_frame = tk.Frame(right_frame)

# 日志内容显示框
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

    # 启动设备的自动化任务
    print(f"启动设备 {device_name} 的自动化任务...")

    # 传递 `desired_caps` 作为 JSON 字符串
    process = subprocess.Popen(
        ['python', 'main.py', json.dumps(desired_caps)],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8'
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
            with log_lock:  # 使用锁确保线程安全
                log_data[device_name] += output
                if current_log_display == device_name:
                    root.after(0, lambda: update_log_text(device_name))  # 使用 after 更新 Tkinter UI
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

        # 改变按钮颜色为灰色，表示设备已停止
        button.config(bg='SystemButtonFace', text=device_name)

# 点击设备按钮时的切换设备状态
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

# 窗口布局
root.update_idletasks()
window_width = root.winfo_width()
window_height = root.winfo_height()
x = 10
y = int((screen_height - window_height) / 2)
root.geometry(f"+{x}+{y}")

# 运行主循环
root.mainloop()
