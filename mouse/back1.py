import keyboard
import time
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import threading
from pynput import keyboard as pynput_keyboard

def start_back_movement(press_duration, release_duration, key):
    is_moving_back = False

    def on_key_press(event):
        nonlocal is_moving_back
        is_moving_back = not is_moving_back
        if is_moving_back:
            print("角色在慢慢后退。")
        else:
            print("角色停止后退。")

    # 监听用户定义的键按下事件
    keyboard.on_press_key(key, on_key_press)

    try:
        while True:
            if is_moving_back:
                keyboard.press('s')
                time.sleep(press_duration / 1000)
                keyboard.release('s')
                time.sleep(release_duration / 1000)
            else:
                time.sleep(0.1)
    except KeyboardInterrupt:
        print("程序被中断")

def on_start_stop():
    global is_running
    if not is_running:
        try:
            key = key_entry.get()
            press_duration = int(press_entry.get())
            release_duration = int(release_entry.get())

            threading.Thread(target=start_back_movement, args=(press_duration, release_duration, key), daemon=True).start()
            start_button.config(text="结束")
            is_running = True
        except ValueError:
            messagebox.showerror("错误", "请输入有效的数字")
    else:
        keyboard.unhook_all()
        start_button.config(text="开始")
        is_running = False

def capture_hotkey():
    """捕获快捷键"""
    key_entry.delete(0, tk.END)
    key_entry.insert(0, "请按下后退快捷键...")
    key_entry.update()

    hotkey = []

    def on_press(key):
        hotkey.append(key)
        return False  # 停止监听

    listener = pynput_keyboard.Listener(on_press=on_press)
    listener.start()
    listener.join()

    key_entry.delete(0, tk.END)
    key_name = '+'.join([str(k).replace("'", "") for k in hotkey])
    key_entry.insert(0, key_name)

# 创建主窗口
root = tk.Tk()
root.title("后退控制设置")

is_running = False

# 创建标签和输入框
ttk.Label(root, text="后退快捷键:").grid(column=0, row=0, padx=10, pady=10)
key_entry = ttk.Entry(root)
key_entry.grid(column=1, row=0, padx=10, pady=10)
set_key_button = ttk.Button(root, text="设置后退快捷键", command=capture_hotkey)
set_key_button.grid(column=2, row=0, padx=10, pady=10)

ttk.Label(root, text="按压时间 (毫秒):").grid(column=0, row=1, padx=10, pady=10)
press_entry = ttk.Entry(root)
press_entry.grid(column=1, row=1, padx=10, pady=10)

ttk.Label(root, text="释放时间 (毫秒):").grid(column=0, row=2, padx=10, pady=10)
release_entry = ttk.Entry(root)
release_entry.grid(column=1, row=2, padx=10, pady=10)

# 创建开始按钮
start_button = ttk.Button(root, text="开始", command=on_start_stop)
start_button.grid(column=0, row=3, columnspan=2, padx=10, pady=10)

# 运行主循环
root.mainloop()
