import json
import time
import threading
import subprocess
import tkinter as tk
from tkinter.scrolledtext import ScrolledText

# 设备运行状态管理（存储设备与其对应的进程）
device_processes = {}
log_data = {}  # 存储设备的日志数据
log_buttons = {}  # 存储日志按钮
current_log_display = None  # 当前显示的日志

# 读取 config.json 配置文件
with open('../config.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

# 创建 GUI
root = tk.Tk()
root.title("设备管理")

# 获取屏幕尺寸
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

# 设置左侧设备区域的最大高度为屏幕高度的80%和最小高度
MAX_HEIGHT = int(screen_height * 0.8)
MIN_HEIGHT = 400  # 设置最小高度

# 创建左侧容器框架
left_frame = tk.Frame(root)
left_frame.pack(side=tk.LEFT, anchor='nw')

# 创建 Canvas 和 Scrollbar
device_canvas = tk.Canvas(left_frame)
device_scrollbar = tk.Scrollbar(left_frame, orient="vertical", command=device_canvas.yview)
device_canvas.configure(yscrollcommand=device_scrollbar.set)

device_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
device_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

# 创建设备列表框架，放置在 Canvas 中
device_frame = tk.Frame(device_canvas)
device_canvas.create_window((0, 0), window=device_frame, anchor='nw')

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

# 调整左侧容器框架的高度和 Canvas 滚动区域
def adjust_left_frame_height(event=None):
    device_frame.update_idletasks()
    total_height = device_frame.winfo_height()
    total_width = device_frame.winfo_width()

    # 使用 MIN_HEIGHT 确保窗口不会太小
    height = max(min(total_height, MAX_HEIGHT), MIN_HEIGHT)

    left_frame.config(height=height, width=total_width + device_scrollbar.winfo_width())
    left_frame.pack_propagate(False)  # 需要设置为 False，以手动控制尺寸

    device_canvas.config(scrollregion=device_canvas.bbox("all"), height=height, width=total_width)
    device_canvas.yview_moveto(0)

# 绑定设备框架大小变化事件
device_frame.bind("<Configure>", adjust_left_frame_height)

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
            print(f"Stopping device {device_name}...")
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
    global current_log_display, log_text  # 将变量设为全局变量

    # 如果设备未启动，初始化为空白日志数据
    if device_name not in log_data:
        log_data[device_name] = ""

    # 如果当前设备的日志已经显示，则隐藏日志框和日志内容
    if current_log_display == device_name:
        # 恢复日志按钮为默认外观
        log_buttons[device_name].config(bg='SystemButtonFace', text='日志')
        log_tab_frame.pack_forget()
        log_display_frame.pack_forget()
        right_frame.pack_forget()  # 隐藏右侧整个日志显示区域
        current_log_display = None
    else:
        # 隐藏当前显示的日志
        if current_log_display:
            log_buttons[current_log_display].config(bg='SystemButtonFace', text='日志')

        # 显示新日志，改变日志按钮为绿色
        log_text.delete(1.0, tk.END)  # 清除现有日志内容
        log_text.insert(tk.END, log_data[device_name])  # 显示当前设备的日志
        log_text.see(tk.END)
        current_log_display = device_name
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)  # 显示右侧区域
        log_tab_frame.pack(side=tk.TOP, fill=tk.X)
        log_display_frame.pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        # 更改日志按钮的颜色并仅显示"日志"
        log_buttons[device_name].config(bg='green', text='日志')

# 获取窗口的宽度和高度
root.update_idletasks()
window_width = root.winfo_width()
window_height = root.winfo_height()

# 计算窗口的位置，使其垂直居中，水平靠左
x = 0  # 设置为0，使窗口位于屏幕左侧
y = int((screen_height - window_height) / 2)

# 设置窗口的位置
root.geometry(f"+{x}+{y}")

# 运行主循环
root.mainloop()
