from explorer import open_explorer

import tkinter as tk
import os
import shutil
import getpass
import platform
import subprocess
import time
import psutil
import wmi
import vlc
import pygetwindow as gw
from PIL import Image, ImageTk

# ====== НАСТРОЙКИ ======
USER = getpass.getuser()
HOST = "root"
current_dir = os.path.abspath(os.environ.get("SystemDrive", "C:") + "\\")

# ====== ИСТОРИЯ КОМАНД ======
command_history = []
history_index = 0
history_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history.txt")

if os.path.exists(history_file):
    with open(history_file, "r", encoding="utf-8") as f:
        command_history = [line.strip() for line in f.readlines()]
    history_index = len(command_history)

# ====== ОКНО ======
root = tk.Tk()
root.attributes("-fullscreen", True)
root.attributes("-topmost", True)
root.overrideredirect(True)
root.configure(bg="black")

# ====== ВЕРХНИЙ БЛОК (ВЫВОД) ======
output = tk.Text(
    root,
    bg="black",
    fg="#ff9d00",
    font=("Consolas", 14),
    border=0,
    state="disabled"
)
output.pack(expand=True, fill="both")

# ====== НИЖНИЙ БЛОК (ВВОД) ======
input_frame = tk.Frame(root, bg="black")
input_frame.pack(fill="x")

prompt_label = tk.Label(
    input_frame,
    text="",
    bg="#1a1a1a",
    fg="#ff9d00",
    font=("Consolas", 14)
)
prompt_label.pack(side="left")

entry = tk.Entry(
    input_frame,
    bg="#1a1a1a",
    fg="#ff9d00",
    insertbackground="#ff9d00",
    font=("Consolas", 14),
    border=0
)
entry.pack(side="left", fill="x", expand=True)
entry.focus()

# ====== ФУНКЦИИ ======
def update_prompt():
    prompt_label.config(text=f"<{USER}@{HOST}> {current_dir}=$ ")

def write(text):
    output.config(state="normal")
    output.insert(tk.END, text)
    output.see(tk.END)
    output.config(state="disabled")

# ====== БЛОКИРОВКА ОКНА ======
def lock_window(window, w=800, h=500, parent=None): # Добавили аргумент parent
    window.transient(parent if parent else root) # Указываем реального родителя
    window.attributes("-topmost", True)
    window.overrideredirect(True)

    screen_w = window.winfo_screenwidth()
    screen_h = window.winfo_screenheight()
    x = (screen_w - w) // 2
    y = (screen_h - h) // 2
    window.geometry(f"{w}x{h}+{x}+{y}")

    window.lift()
    window.focus_force()

    def close_and_focus():
        window.destroy()
        if parent:
            parent.lift() # Поднимаем родителя (например, проводник)
            parent.focus_force()
        else:
            entry.focus_force() # Если родителя нет, возвращаем в терминал

    window.bind("<Escape>", lambda e: close_and_focus())
    return close_and_focus

# ===== ЗАКРЫТИЕ ПРИЛОЖЕНИЯ ======
def on_closing():
    if os.path.exists(history_file):
        os.remove(history_file)
    root.destroy()

# ====== КАСТОМНЫЙ ТИТЛБАР ======
def make_titlebar(window, title="Window", close_command=None):
    bg_color = "#1a1a1a"
    accent_color = "#ff9d00"

    titlebar = tk.Frame(window, bg=bg_color, height=30)
    titlebar.pack(fill="x", side="top")
    titlebar.pack_propagate(False)

    # Название окна
    title_label = tk.Label(
        titlebar, 
        text=f" 🖥️ {title}",
        bg=bg_color, 
        fg=accent_color,
        font=("Consolas", 10, "bold")
    )
    title_label.pack(side="left", padx=5)

    # Кнопка закрытия (использует переданную команду)
    cmd = close_command if close_command else window.destroy
    close_btn = tk.Button(
        titlebar, 
        text=" [X] ",
        bg=bg_color, 
        fg=accent_color,
        font=("Consolas", 10, "bold"),
        border=0,
        activebackground="#ff3333",
        activeforeground="white",
        command=cmd
    )
    close_btn.pack(side="right", padx=5)

    # Логика перемещения окна
    def start_move(event):
        window.x = event.x
        window.y = event.y

    def do_move(event):
        x = event.x_root - window.x
        y = event.y_root - window.y
        window.geometry(f"+{x}+{y}")

    titlebar.bind("<ButtonPress-1>", start_move)
    titlebar.bind("<B1-Motion>", do_move)
    title_label.bind("<ButtonPress-1>", start_move)
    title_label.bind("<B1-Motion>", do_move)

    # Оранжевая рамка для всего окна
    window.config(highlightbackground=accent_color, highlightthickness=1)

    return title_label

# ====== СПРАВКА ======
def help():
    write("\nAvailable commands:\n")
    write("--------------------------------------------------\n")
    write("ls        - show files and folders in current directory\n")
    write("pwd       - show current directory path\n")
    write("cd <dir>  - change directory\n")
    write("mkdir <n> - create a new folder\n")
    write("rm <n>    - delete file or folder\n")
    write("clear     - clear terminal screen\n")
    write("file      - open file explorer\n")
    write("open <f>  - open image file\n")
    write("bazfetch  - show system information and BazOS logo\n")
    write("exit      - exit from terminal\n")
    write("help      - show this help message\n")
    write("--------------------------------------------------\n\n")

# ====== БЛОКНОТ (nano) ======
def nano(filename, parent_window=None):
    full_path = os.path.join(current_dir, filename)
    editor = tk.Toplevel(root)
    
    # Передаем родителя
    close_cmd = lock_window(editor, 700, 500, parent=parent_window)
    make_titlebar(editor, title=f"nano - {filename}", close_command=close_cmd)
    
    editor.configure(bg="black")
    text_widget = tk.Text(editor, bg="black", fg="#ff9d00", insertbackground="#ff9d00", font=("Consolas", 13), border=0, padx=10, pady=10)
    text_widget.pack(expand=True, fill="both")

    if os.path.exists(full_path):
        with open(full_path, "r", encoding="utf-8") as f:
            text_widget.insert("1.0", f.read())

    def save():
        with open(full_path, "w", encoding="utf-8") as f:
            f.write(text_widget.get("1.0", "end-1c"))
        write(f"nano: {filename} saved.\n")

    help_bar = tk.Frame(editor, bg="#1a1a1a")
    help_bar.pack(fill="x", side="bottom")
    tk.Label(help_bar, text=" [Ctrl+S] Save  [Ctrl+X] Exit ", bg="#1a1a1a", fg="#ff9d00", font=("Consolas", 9)).pack(pady=2)

    editor.bind("<Control-s>", lambda e: save())
    editor.bind("<Control-x>", lambda e: close_cmd())
    text_widget.focus_set()

# ====== ИНФОРМАЦИЯ О ВИДЕОКАРТЕ ======
def get_gpu_info():
    try:
        c = wmi.WMI()
        gpus = c.Win32_VideoController()

        if not gpus:
            return "Unknown", "Unknown"

        gpu = gpus[0]
        name = gpu.Name

        if gpu.AdapterRAM:
            vram = int(gpu.AdapterRAM) // (1024 ** 2)
            vram = f"{vram} MB"
        else:
            vram = "Unknown"

        return name, vram
    except Exception:
        return "Unknown", "Unknown"

# ====== BAZFETCH ======
def bazfetch():
    logo = [
        "██████████████████",
        "███    ████    ███",
        "█  ████    ████  █",
        "█  ████████████  █",
        "███  ████████  ███",
        "█████  ████  █████",
        "███████    ███████",
        "██████████████████",
        "██████BazOSx██████",
        "██████████████████",
    ]

    uname = platform.uname()
    mem = psutil.virtual_memory()
    gpu_name, gpu_vram = get_gpu_info()

    ram_total = mem.total // (1024 ** 3)
    ram_used = mem.used // (1024 ** 3)
    cpu_usage = psutil.cpu_percent(interval=0.5)

    info = [
        f"User: {USER}",
        f"Host: {HOST}",
        f"OS: {uname.system} {uname.release}",
        f"Kernel: {uname.version}",
        f"GPU: {gpu_name}",
        f"CPU: {uname.processor}",
        f"CPU Load: {cpu_usage}%",
        f"RAM: {ram_used}GB / {ram_total}GB",
        f"VRAM: {gpu_vram}",
        f"Shell: bazOS",
    ]

    write("\n")
    for i in range(max(len(logo), len(info))):
        left = logo[i] if i < len(logo) else " " * 12
        right = info[i] if i < len(info) else ""
        write(f"{left}   {right}\n")
    write("\n")

# ====== УНИВЕРСАЛЬНЫЙ МЕДИАПЛЕЕР (ФОТО И ВИДЕО) ======
def open_media(file_path, parent_window=None):
    full_path = os.path.abspath(os.path.join(current_dir, file_path))
    if not os.path.isfile(full_path):
        write(f"open: {file_path} does not exist\n")
        return

    ext = os.path.splitext(full_path)[1].lower()
    media_window = tk.Toplevel(root)
    media_window.configure(bg="black")
    
    # Переменная для плеера, чтобы она была доступна в функции закрытия
    player_handle = [None] 

    # 1. Создаем функцию закрытия, которая сначала стопает VLC, а потом удаляет окно
    def on_close():
        if player_handle[0]:
            player_handle[0].stop()  # Останавливаем звук и видео
        
        # Вызываем стандартную логику закрытия (фокус и destroy)
        # Мы достаем её позже из lock_window
        actual_close_logic()

    # 2. Инициализируем lock_window (пока без реальной логики закрытия)
    actual_close_logic = lock_window(media_window, 800, 600, parent=parent_window)
    
    # 3. Передаем нашу навороченную on_close в титлбар
    make_titlebar(media_window, title=f"BazOS Media - {os.path.basename(file_path)}", close_command=on_close)

    canvas = tk.Canvas(media_window, bg="black", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    if ext in [".mp4", ".avi", ".mkv", ".mov"]:
        instance = vlc.Instance("--no-xlib")
        player = instance.media_player_new()
        player_handle[0] = player # Сохраняем ссылку для on_close
        
        player.set_hwnd(canvas.winfo_id())
        media = instance.media_new(full_path)
        player.set_media(media)
        player.play()

        # Дублируем закрытие на Escape
        media_window.bind("<Escape>", lambda e: on_close())
    else:
        # Логика для картинок (тут плеер не нужен)
        try:
            img = Image.open(full_path)
            img_width, img_height = img.size
            def resize_image(event):
                if event.width < 1 or event.height < 1: return
                ratio = min(event.width / img_width, event.height / img_height)
                resized = img.resize((int(img_width * ratio), int(img_height * ratio)), Image.LANCZOS)
                photo = ImageTk.PhotoImage(resized)
                canvas.delete("all")
                canvas.create_image(event.width//2, event.height//2, anchor="center", image=photo)
                canvas.image = photo
            canvas.bind("<Configure>", resize_image)
        except Exception as e:
            write(f"open: error {e}\n")

# ====== АВТОДОПОЛНЕНИЕ ======
def autocomplete(event=None):
    text = entry.get()
    if not text:
        return "break"

    if os.path.sep in text:
        dir_name = os.path.dirname(text)
        prefix = os.path.basename(text)
        dir_path = os.path.abspath(os.path.join(current_dir, dir_name))
    else:
        dir_name = ""
        prefix = text
        dir_path = current_dir

    try:
        matches = [f for f in os.listdir(dir_path) if f.startswith(prefix)]
    except Exception:
        matches = []

    if len(matches) == 1:
        new_text = os.path.join(dir_name, matches[0]) if dir_name else matches[0]
        entry.delete(0, tk.END)
        entry.insert(0, new_text)
    elif len(matches) > 1:
        write("Possible completions:\n")
        for m in matches:
            write(m + "\n")
    return "break"

# ====== ИСТОРИЯ КОМАНД ======
def history_up(event=None):
    global history_index
    if command_history and history_index > 0:
        history_index -= 1
        entry.delete(0, tk.END)
        entry.insert(0, command_history[history_index])
    return "break"

def history_down(event=None):
    global history_index
    if command_history and history_index < len(command_history) - 1:
        history_index += 1
        entry.delete(0, tk.END)
        entry.insert(0, command_history[history_index])
    else:
        entry.delete(0, tk.END)
        history_index = len(command_history)
    return "break"

# ====== КОМАНДЫ ТЕРМИНАЛА ======
def run_command(event=None):
    global current_dir, history_index

    full_cmd = entry.get().strip()   # <-- ВОТ ТУТ
    entry.delete(0, tk.END)

    write(f"<{USER}@{HOST}> {current_dir}=$ {full_cmd}\n")

    if not full_cmd:
        return

    # разбиваем по ;
    commands = [c.strip() for c in full_cmd.split(";") if c.strip()]

    # сохраняем в историю всю строку целиком
    command_history.append(full_cmd)
    history_index = len(command_history)
    with open(history_file, "a", encoding="utf-8") as f:
        f.write(full_cmd + "\n")


    for cmd in commands:
        parts = cmd.split()
        command = parts[0]

        try:
            if command == "ls":
                for f in os.listdir(current_dir):
                    write(f + "\n")

            elif command == "pwd":
                write(current_dir + "\n")

            elif command == "cd":
                if len(parts) > 1:
                    new_path = os.path.abspath(os.path.join(current_dir, parts[1]))
                    if os.path.isdir(new_path):
                        current_dir = new_path
                        update_prompt()
                    else:
                        write("cd: no such directory\n")

            elif command == "mkdir":
                os.mkdir(os.path.join(current_dir, parts[1]))

            elif command == "rm":
                target = os.path.join(current_dir, parts[1])
                if os.path.isdir(target):
                    shutil.rmtree(target)
                else:
                    os.remove(target)

            elif command == "clear":
                output.config(state="normal")
                output.delete("1.0", tk.END)
                output.config(state="disabled")

            elif command == "nano":
                if len(parts) > 1:
                    nano(parts[1])
                else:
                    write("Usage: nano <filename>\n")

            elif command == "python":
                if len(parts) > 1:
                    script_path = os.path.join(current_dir, parts[1])
                    if os.path.exists(script_path):
                        try:
                            # Запуск скрипта
                            result = subprocess.run(
                                ["python", script_path],
                                capture_output=True,
                                text=True,
                                cwd=current_dir
                            )
                            if result.stdout:
                                write(result.stdout + "\n")
                            if result.stderr:
                                write(result.stderr + "\n")
                        except Exception as e:
                            write(f"python: error running script: {e}\n")
                    else:
                        write(f"python: {parts[1]} not found\n")
                else:
                    write("Usage: python <script.py>\n")


            elif command == "file":
                open_explorer(
                    current_dir, 
                    root, 
                    lock_window, 
                    make_titlebar, 
                    entry, 
                    write, 
                    nano, 
                    current_dir, 
                    open_media)

            elif command == "open":
                if len(parts) > 1:
                    open_media(parts[1])
                else:
                    write("open: specify a file\n")

            elif command == "bazfetch":
                bazfetch()

            elif command == "help":
                help()

            elif command == "exit":
                on_closing()

            else:
                write(f"{command}: command not found\n")

        except Exception as e:
            write(f"error: {e}\n")

# ====== БИНДЫ ======
entry.bind("<Return>", run_command)
entry.bind("<Tab>", autocomplete)
entry.bind("<Up>", history_up)
entry.bind("<Down>", history_down)
root.bind("<Escape>", lambda e: on_closing())
root.protocol("WM_DELETE_WINDOW", on_closing)

update_prompt()
root.mainloop()
