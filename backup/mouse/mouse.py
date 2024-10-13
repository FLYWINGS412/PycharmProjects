import time
import ctypes
import random
import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pynput import keyboard as pynput_keyboard
import keyboard as kb

# 加载user32.dll，用于模拟点击
user32 = ctypes.windll.user32

# 线程控制标志
clicking_left = False
clicking_right = False
hotkeys_enabled = False
left_hotkey = set()
right_hotkey = set()
back_hotkey = set()
current_keys = set()

# 用于存储监听器对象
keyboard_listener = None
is_running = False
is_moving_back = False

def display_status(message):
    """在屏幕右下角显示状态信息"""
    root = tk.Toplevel()
    root.overrideredirect(1)
    root.attributes('-topmost', 1)
    root.attributes('-alpha', 0.7)
    label = tk.Label(root, text=message, bg='black', fg='red', font=('Helvetica', 24))  # 字体增大1倍，颜色改为红色
    label.pack()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    root.geometry(f"+{screen_width - 300}+{screen_height - 100}")  # 调整位置以适应增大的字体
    root.after(1000, root.destroy)

def click_mouse_left():
    """左键点击操作，按指定间隔进行点击"""
    while clicking_left:
        user32.mouse_event(2, 0, 0, 0, 0)  # 鼠标左键按下
        user32.mouse_event(4, 0, 0, 0, 0)  # 鼠标左键松开
        interval = 1 / clicks_per_second + random.uniform(-0.01, 0.01)  # 引入随机延迟
        time.sleep(interval)

def click_mouse_right():
    """右键点击操作，按指定间隔进行点击"""
    while clicking_right:
        user32.mouse_event(8, 0, 0, 0, 0)  # 鼠标右键按下
        user32.mouse_event(16, 0, 0, 0, 0)  # 鼠标右键松开
        interval = 1 / clicks_per_second + random.uniform(-0.01, -0.01)  # 引入随机延迟
        time.sleep(interval)

def toggle_clicking_left():
    """切换左键点击状态"""
    global clicking_left, clicks_per_second
    if clicking_left:
        clicking_left = False
        message = "停止 左键自动点击"
    else:
        clicks_per_second = int(clicks_entry.get())
        if clicks_per_second <= 0:
            raise ValueError("点击次数必须大于0。")
        clicking_left = True
        threading.Thread(target=click_mouse_left).start()
        message = "开始 左键自动点击"
    display_status(message)
    print(message)

def toggle_clicking_right():
    """切换右键点击状态"""
    global clicking_right, clicks_per_second
    if clicking_right:
        clicking_right = False
        message = "停止 右键自动点击"
    else:
        clicks_per_second = int(clicks_entry.get())
        if clicks_per_second <= 0:
            raise ValueError("点击次数必须大于0。")
        clicking_right = True
        threading.Thread(target=click_mouse_right).start()
        message = "开始 右键自动点击"
    display_status(message)
    print(message)

def on_press(key):
    """按键按下事件处理"""
    if hotkeys_enabled:
        key_name = key.char if hasattr(key, 'char') else key.name
        current_keys.add(key_name)
        check_combinations()

def on_release(key):
    """按键释放事件处理"""
    if hotkeys_enabled:
        key_name = key.char if hasattr(key, 'char') else key.name
        current_keys.discard(key_name)

def check_combinations():
    """检查当前按键的组合"""
    if left_hotkey and left_hotkey.issubset(current_keys):
        toggle_clicking_left()
    if right_hotkey and right_hotkey.issubset(current_keys):
        toggle_clicking_right()
    if back_hotkey and back_hotkey.issubset(current_keys):
        toggle_back_movement()

def disable_entries():
    """禁用所有输入框"""
    clicks_entry.config(state='disabled')
    left_hotkey_entry.config(state='disabled')
    right_hotkey_entry.config(state='disabled')
    back_hotkey_entry.config(state='disabled')
    press_entry.config(state='disabled')
    release_entry.config(state='disabled')

def enable_entries():
    """启用所有输入框"""
    clicks_entry.config(state='normal')
    left_hotkey_entry.config(state='normal')
    right_hotkey_entry.config(state='normal')
    back_hotkey_entry.config(state='normal')
    press_entry.config(state='normal')
    release_entry.config(state='normal')

def capture_hotkey(entry, action):
    """捕获快捷键"""
    disable_entries()
    entry.delete(0, tk.END)
    entry.insert(0, f"请按下{action}快捷键...")
    entry.update()

    hotkey = set()
    captured = False

    def on_press(key):
        nonlocal captured
        key_name = key.char if hasattr(key, 'char') else key.name
        hotkey.add(key_name)
        captured = True
        print(f"捕获到按键: {key_name}")
        return False  # 停止监听

    # 隐藏主窗口
    root.withdraw()
    print("主窗口已隐藏，开始捕获快捷键")

    listener_keyboard = pynput_keyboard.Listener(on_press=on_press)
    listener_keyboard.start()
    listener_keyboard.join()

    # 恢复主窗口
    root.deiconify()
    print("捕获结束，恢复主窗口")

    if captured:
        hotkey_str = '+'.join(hotkey)
        print(f"捕获到的快捷键: {hotkey_str}")

        def update_entry():
            entry.delete(0, tk.END)
            entry.insert(0, hotkey_str)
            print(f"快捷键设置为: {hotkey_str}")

        # 在主线程中更新Entry
        root.after(0, update_entry)
        enable_entries()
        return hotkey
    else:
        messagebox.showwarning("警告", "未捕获到快捷键，请重试。")
        print("未捕获到快捷键")
        enable_entries()
        return set()

def set_left_hotkey():
    """设置左键快捷键"""
    global left_hotkey
    print("开始设置左键快捷键")
    left_hotkey = capture_hotkey(left_hotkey_entry, "左键")
    if left_hotkey:
        display_status("左键快捷键设置成功")
        print("左键快捷键设置成功")

def set_right_hotkey():
    """设置右键快捷键"""
    global right_hotkey
    print("开始设置右键快捷键")
    right_hotkey = capture_hotkey(right_hotkey_entry, "右键")
    if right_hotkey:
        display_status("右键快捷键设置成功")
        print("右键快捷键设置成功")

def set_back_hotkey():
    """设置后退快捷键"""
    global back_hotkey
    print("开始设置后退快捷键")
    back_hotkey = capture_hotkey(back_hotkey_entry, "后退")
    if back_hotkey:
        display_status("后退快捷键设置成功")
        print("后退快捷键设置成功")

def toggle_program():
    """启用或禁用程序"""
    global hotkeys_enabled, keyboard_listener
    if hotkeys_enabled:
        hotkeys_enabled = False
        if keyboard_listener is not None:
            keyboard_listener.stop()
        toggle_button.config(text="开始")
        print("程序已停止")
    else:
        hotkeys_enabled = True
        keyboard_listener = pynput_keyboard.Listener(on_press=on_press, on_release=on_release)
        keyboard_listener.start()
        toggle_button.config(text="关闭")
        print("程序已启动")

def start_back_movement(press_duration, release_duration):
    """开始后退移动"""
    global is_moving_back
    while is_moving_back:
        kb.press('s')
        time.sleep(press_duration / 1000)
        kb.release('s')
        time.sleep(release_duration / 1000)

def toggle_back_movement():
    """切换后退移动状态"""
    global is_moving_back
    is_moving_back = not is_moving_back
    if is_moving_back:
        press_duration = int(press_entry.get())
        release_duration = int(release_entry.get())
        threading.Thread(target=start_back_movement, args=(press_duration, release_duration), daemon=True).start()
        message = "开始 自动后退"
    else:
        message = "停止 自动后退"
    display_status(message)
    print(message)

def on_start_stop():
    """开始或停止后退移动"""
    global is_running
    if not is_running:
        try:
            press_duration = int(press_entry.get())
            release_duration = int(release_entry.get())
            threading.Thread(target=start_back_movement, args=(press_duration, release_duration), daemon=True).start()
            back_start_button.config(text="结束")
            is_running = True
            print("开始自动后退")
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
    else:
        is_running = False
        print("停止自动后退")

# 创建主窗口
root = tk.Tk()
root.title("《我的世界》辅助工具")

# 创建和放置控件
tk.Label(root, text="每秒点击次数:").grid(row=0, column=0, padx=10, pady=10)
clicks_entry = tk.Entry(root)
clicks_entry.grid(row=0, column=1, padx=10, pady=10)

tk.Label(root, text="左键快捷键:").grid(row=1, column=0, padx=10, pady=10)
left_hotkey_entry = tk.Entry(root)
left_hotkey_entry.grid(row=1, column=1, padx=10, pady=10)
set_left_hotkey_button = tk.Button(root, text="设置左键快捷键", command=set_left_hotkey)
set_left_hotkey_button.grid(row=1, column=2, padx=10, pady=10)

tk.Label(root, text="右键快捷键:").grid(row=2, column=0, padx=10, pady=10)
right_hotkey_entry = tk.Entry(root)
right_hotkey_entry.grid(row=2, column=1, padx=10, pady=10)
set_right_hotkey_button = tk.Button(root, text="设置右键快捷键", command=set_right_hotkey)
set_right_hotkey_button.grid(row=2, column=2, padx=10, pady=10)

toggle_button = tk.Button(root, text="开始", command=toggle_program, width=12, height=2)
toggle_button.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

# 创建后退部分控件
ttk.Label(root, text="后退快捷键:").grid(column=0, row=4, padx=10, pady=10)
back_hotkey_entry = ttk.Entry(root)
back_hotkey_entry.grid(column=1, row=4, padx=10, pady=10)
set_back_hotkey_button = tk.Button(root, text="设置后退快捷键", command=set_back_hotkey)
set_back_hotkey_button.grid(column=2, row=4, padx=10, pady=10)

ttk.Label(root, text="按压时间 (毫秒):").grid(column=0, row=5, padx=10, pady=10)
press_entry = ttk.Entry(root)
press_entry.grid(column=1, row=5, padx=10, pady=10)

ttk.Label(root, text="释放时间 (毫秒):").grid(column=0, row=6, padx=10, pady=10)
release_entry = ttk.Entry(root)
release_entry.grid(column=1, row=6, padx=10, pady=10)

back_start_button = tk.Button(root, text="开始", command=on_start_stop, width=12, height=2)
back_start_button.grid(column=0, row=7, columnspan=3, padx=10, pady=10)

# 运行主循环
root.mainloop()
