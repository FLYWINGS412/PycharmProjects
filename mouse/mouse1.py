import time
import ctypes
import threading
import tkinter as tk
from tkinter import messagebox
from pynput import keyboard as pynput_keyboard

# 加载user32.dll，用于模拟点击
user32 = ctypes.windll.user32

# 线程控制标志
clicking_left = False
clicking_right = False
hotkeys_enabled = False
left_hotkey = set()
right_hotkey = set()
current_keys = set()

# 用于存储监听器对象
keyboard_listener = None

def click_mouse_left(interval):
    """左键点击操作，按指定间隔进行点击"""
    next_click = time.time()
    while clicking_left:
        user32.mouse_event(2, 0, 0, 0, 0)  # 鼠标左键按下
        user32.mouse_event(4, 0, 0, 0, 0)  # 鼠标左键松开
        next_click += interval
        sleep_time = next_click - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)

def click_mouse_right(interval):
    """右键点击操作，按指定间隔进行点击"""
    next_click = time.time()
    while clicking_right:
        user32.mouse_event(8, 0, 0, 0, 0)  # 鼠标右键按下
        user32.mouse_event(16, 0, 0, 0, 0)  # 鼠标右键松开
        next_click += interval
        sleep_time = next_click - time.time()
        if sleep_time > 0:
            time.sleep(sleep_time)

def toggle_clicking_left():
    """切换左键点击状态"""
    global clicking_left
    if clicking_left:
        clicking_left = False
        print("停止左键自动点击。")
    else:
        clicks_per_second = int(clicks_entry.get())
        if clicks_per_second <= 0:
            raise ValueError("点击次数必须大于0。")
        click_interval = 1 / clicks_per_second
        clicking_left = True
        threading.Thread(target=click_mouse_left, args=(click_interval,)).start()
        print("开始左键自动点击。")

def toggle_clicking_right():
    """切换右键点击状态"""
    global clicking_right
    if clicking_right:
        clicking_right = False
        print("停止右键自动点击。")
    else:
        clicks_per_second = int(clicks_entry.get())
        if clicks_per_second <= 0:
            raise ValueError("点击次数必须大于0。")
        click_interval = 1 / clicks_per_second
        clicking_right = True
        threading.Thread(target=click_mouse_right, args=(click_interval,)).start()
        print("开始右键自动点击。")

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

def capture_hotkey(entry, action):
    """捕获快捷键"""
    entry.delete(0, tk.END)
    entry.insert(0, f"请按下{action}快捷键...")
    entry.update()

    hotkey = set()
    capturing = True

    def on_press(key):
        key_name = key.char if hasattr(key, 'char') else key.name
        hotkey.add(key_name)
        return True

    def on_release(key):
        nonlocal capturing
        capturing = False
        return False

    listener_keyboard = pynput_keyboard.Listener(on_press=on_press, on_release=on_release)
    listener_keyboard.start()
    listener_keyboard.join()

    entry.delete(0, tk.END)
    hotkey_str = '+'.join(hotkey)
    entry.insert(0, hotkey_str)
    return hotkey

def set_left_hotkey():
    """设置左键快捷键"""
    global left_hotkey
    left_hotkey = capture_hotkey(left_hotkey_entry, "左键")
    messagebox.showinfo("快捷键设置", f"左键快捷键: {'+'.join(left_hotkey)}")

def set_right_hotkey():
    """设置右键快捷键"""
    global right_hotkey
    right_hotkey = capture_hotkey(right_hotkey_entry, "右键")
    messagebox.showinfo("快捷键设置", f"右键快捷键: {'+'.join(right_hotkey)}")

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

# 创建主窗口
root = tk.Tk()
root.title("鼠标连点器")

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

toggle_button = tk.Button(root, text="开始", command=toggle_program, font=('Helvetica', 14), width=10, height=2)
toggle_button.grid(row=3, column=1, padx=10, pady=20)

# 运行主循环
root.mainloop()
