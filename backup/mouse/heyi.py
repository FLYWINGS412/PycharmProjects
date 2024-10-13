import time
import ctypes
import random
import threading
import tkinter as tk
from tkinter import ttk
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
        interval = 1 / clicks_per_second + random.uniform(-0.01, 0.01)  # 引入随机延迟
        time.sleep(interval)

def toggle_clicking_left():
    """切换左键点击状态"""
    global clicking_left, clicks_per_second
    if clicking_left:
        clicking_left = False
        print("停止  左键自动点击")
    else:
        clicks_per_second = int(clicks_entry.get())
        if clicks_per_second <= 0:
            raise ValueError("点击次数必须大于0。")
        clicking_left = True
        threading.Thread(target=click_mouse_left).start()
        print("开始  左键自动点击")

def toggle_clicking_right():
    """切换右键点击状态"""
    global clicking_right, clicks_per_second
    if clicking_right:
        clicking_right = False
        print("停止  右键自动点击")
    else:
        clicks_per_second = int(clicks_entry.get())
        if clicks_per_second <= 0:
            raise ValueError("点击次数必须大于0。")
        clicking_right = True
        threading.Thread(target=click_mouse_right).start()
        print("开始  右键自动点击")

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

def capture_hotkey(entry, action):
    """捕获快捷键"""
    # 将主窗口置于不可见状态
    root.withdraw()

    entry.delete(0, tk.END)
    entry.insert(0, f"请按下{action}快捷键...")
    entry.update()

    hotkey = set()

    def on_press(key):
        key_name = key.char if hasattr(key, 'char') else key.name
        hotkey.add(key_name)
        return False  # 停止监听

    listener_keyboard = pynput_keyboard.Listener(on_press=on_press)
    listener_keyboard.start()
    listener_keyboard.join()

    entry.delete(0, tk.END)
    hotkey_str = '+'.join(hotkey)
    entry.insert(0, hotkey_str)

    # 恢复主窗口可见状态
    root.deiconify()

    return hotkey

def set_left_hotkey():
    """设置左键快捷键"""
    global left_hotkey
    left_hotkey = capture_hotkey(left_hotkey_entry, "左键")

def set_right_hotkey():
    """设置右键快捷键"""
    global right_hotkey
    right_hotkey = capture_hotkey(right_hotkey_entry, "右键")

def set_back_hotkey():
    """设置后退快捷键"""
    global back_hotkey
    back_hotkey = capture_hotkey(back_hotkey_entry, "后退")

def toggle_program():
    """启用或禁用程序"""
    global hotkeys_enabled, keyboard_listener
    if hotkeys_enabled:
        hotkeys_enabled = False
        if keyboard_listener is not None:
            keyboard_listener.stop()
        toggle_button.config(text="开始")
    else:
        hotkeys_enabled = True
        keyboard_listener = pynput_keyboard.Listener(on_press=on_press, on_release=on_release)
        keyboard_listener.start()
        toggle_button.config(text="关闭")

def start_back_movement(press_duration, release_duration, key):
    """开始后退移动"""
    global is_moving_back
    is_moving_back = False

    def on_key_press(event):
        global is_moving_back
        is_moving_back = not is_moving_back
        if is_moving_back:
            print("开始  自动后退")
        else:
            print("停止  自动后退")

    # 监听用户定义的键按下事件
    kb.on_press_key(key, on_key_press)

    try:
        while True:
            if is_moving_back:
                kb.press('s')
                time.sleep(press_duration / 1000)
                kb.release('s')
                time.sleep(release_duration / 1000)
            else:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("程序被中断")

def on_start_stop():
    """开始或停止后退移动"""
    global is_running
    if not is_running:
        try:
            key = back_hotkey_entry.get()
            press_duration = int(press_entry.get())
            release_duration = int(release_entry.get())

            threading.Thread(target=start_back_movement, args=(press_duration, release_duration, key), daemon=True).start()
            back_start_button.config(text="结束")
            is_running = True
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
    else:
        kb.unhook_all()
        back_start_button.config(text="开始")
        is_running = False

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
