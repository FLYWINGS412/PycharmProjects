import json
import time
import threading
import subprocess
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

# 设备运行状态管理（存储设备与其对应的进程）
device_processes = {}
log_data = {}  # 存储设备的日志数据
log_buttons = {}  # 存储日志标签按钮
current_log_display = None  # 当前显示的日志
log_text = None  # 全局日志文本框
log_tab_frame = None  # 全局日志标签框
log_display_frame = None  # 全局日志显示框

# 读取 config.json 配置文件
with open('../config.json', 'r') as f:
    config = json.load(f)

# 启动设备
def start_device(device_name, button):
    device_info = config.get(device_name)

    if not device_info:
        raise ValueError(f"Device '{device_name}' not found in config.json")

    # 启动设备的自动化任务
    print(f"启动设备 {device_name}...")

    # 设置编码为 'utf-8'，避免 gbk 编码问题
    process = subprocess.Popen(['python', 'main.py'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding='utf-8')

    # 将设备和进程映射存储
    device_processes[device_name] = process

    # 初始化日志数据
    log_data[device_name] = ""

    # 改变按钮颜色为绿色，表示设备启动，并显示设备名
    button.config(bg='green', text=f'{device_name}')

    # 实时更新日志
    def update_log():
        while process.poll() is None:
            output = process.stdout.readline()
            if output:
                log_data[device_name] += output  # 保存日志数据
                if current_log_display == device_name:
                    log_text.delete(1.0, tk.END)  # 清除当前内容
                    log_text.insert(tk.END, log_data[device_name])  # 插入最新内容
                    log_text.see(tk.END)
            time.sleep(0.1)  # 每100ms检查一次日志输出

    # 启动日志更新线程
    threading.Thread(target=update_log, daemon=True).start()

# 停止设备
def stop_device(device_name, button):
    if device_name in device_processes:
        process = device_processes[device_name]
        if process.poll() is None:  # 进程仍在运行
            process.terminate()
            print(f"停止设备 {device_name}...")
        del device_processes[device_name]

        # 改变按钮颜色为灰色，表示设备已停止，并显示设备名
        button.config(bg='SystemButtonFace', text=device_name)

# 点击设备按钮时的行为
def toggle_device(device_name, button):
    if device_name in device_processes:
        stop_device(device_name, button)
    else:
        start_device(device_name, button)

# 显示或隐藏日志标签和内容
def show_or_hide_log(device_name):
    global current_log_display  # 将 current_log_display 设为全局变量

    # 如果设备未启动，初始化为空白日志数据
    if device_name not in log_data:
        log_data[device_name] = ""

    # 如果当前设备的日志已经显示，则隐藏日志框和日志内容
    if current_log_display == device_name:
        # 隐藏日志框和日志内容
        log_tab_frame.pack_forget()
        log_display_frame.pack_forget()  # 隐藏日志标签框和内容
        right_frame.pack_forget()  # 隐藏右侧整个日志显示区域
        current_log_display = None
    else:
        # 如果当前没有显示日志，则重新显示日志框和内容
        log_text.delete(1.0, tk.END)  # 清除现有日志内容
        log_text.insert(tk.END, log_data[device_name])  # 显示当前设备的日志
        log_text.see(tk.END)
        current_log_display = device_name
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)  # 显示右侧区域
        log_tab_frame.pack(side=tk.TOP, fill=tk.X)  # 显示日志标签
        log_display_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)  # 显示日志内容框

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

# 将滚动条嵌入到设备画布中，这样滚动条不会影响右侧的布局
device_canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
device_canvas.configure(yscrollcommand=device_scrollbar.set)

# 更新布局参数，确保填满垂直区域
device_frame.pack(side=tk.LEFT, fill=tk.Y, expand=False)
device_canvas.pack(side=tk.LEFT, fill=tk.Y, expand=False)
device_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

# 创建右侧显示区域，包含日志标签和日志显示框
right_frame = tk.Frame(root)
right_frame.pack_forget()  # 初始状态不占用空间

# 日志标签框，初始状态隐藏
log_tab_frame = tk.Frame(right_frame)
log_display_frame = tk.Frame(right_frame)

# 日志内容显示框
log_text = ScrolledText(log_display_frame, height=20, wrap=tk.WORD)
log_text.pack(fill=tk.BOTH, expand=True)

# 为每个设备创建按钮和日志按钮
device_buttons = {}
for device_name in config.keys():
    # 使用 device_name 显示按钮名
    frame = tk.Frame(scrollable_frame)
    frame.pack(fill=tk.X, pady=2)  # 调整 pady 减少垂直间距

    # 设备按钮
    device_button = tk.Button(frame, text=device_name, width=12)  # 调整按钮的宽度
    device_button.pack(side=tk.LEFT, padx=5)  # 调整 padx 减少按钮左右空余

    # 创建日志按钮
    log_button = tk.Button(frame, text="日志", width=5)  # 调整日志按钮的宽度
    log_button.pack(side=tk.RIGHT, padx=5)  # 减少日志按钮左右空余

    # 设备按钮点击事件
    device_button.config(command=lambda name=device_name, btn=device_button: toggle_device(name, btn))

    # 日志按钮点击事件
    log_button.config(command=lambda name=device_name: show_or_hide_log(name))

    device_buttons[device_name] = device_button

# 运行主循环
root.mainloop()
