from explorer import open_explorer
from media import open_media
from archive import open_archive

import tkinter as tk
import os
import psutil
import wmi
import platform
import random
import shutil
import getpass
import GPUtil  # Добавляем для GPU
from datetime import datetime
import platform
import subprocess
import psutil
import wmi
import pygetwindow as gw


# ====== ЦВЕТА ======
colors = {"orange": "#ff9d00"}

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
    fg=colors["orange"],
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
    fg=colors["orange"],
    font=("Consolas", 14)
)
prompt_label.pack(side="left")

entry = tk.Entry(
    input_frame,
    bg="#1a1a1a",
    fg=colors["orange"],
    insertbackground=colors["orange"],
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

# ====== ПЛАВНЫЙ ЭФФЕКТ МАТРИЦЫ ======
def matrix_effect():
    matrix_win = tk.Toplevel(root)
    matrix_win.attributes("-fullscreen", True)
    matrix_win.attributes("-topmost", True)
    matrix_win.configure(bg="black")
    matrix_win.config(cursor="none")
    
    canvas = tk.Canvas(matrix_win, bg="black", highlightthickness=0)
    canvas.pack(fill="both", expand=True)

    width = matrix_win.winfo_screenwidth()
    height = matrix_win.winfo_screenheight()
    
    font_size = 20
    columns = int(width / font_size)
    
    # Скорость падения (в пикселях за кадр)
    speed = 10 
    # Список для хранения данных о каждой колонке: [текущая_y, список_id_текста]
    # На старте разбрасываем их по высоте рандомно
    column_data = []
    
    chars = "ｱｲｳｴｵｶｷｸｹｺｻｼｽｾｿﾀﾁﾂﾃﾄﾅﾆﾇﾈﾉﾊﾋﾌﾍﾎﾏﾐﾑﾒﾓ1234567890abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ@#$%^&*()阿吽空風火水土龍虎犬猫蛇蟲魚鳥あいうえおかきくけこさしすせそたちつてとなにぬねのはひふへほまみむめもабвгдеёжзийклмнопрстуфхцчшщъыьэюяїєіїABCDEFGHIJKLMNOPQRSTUVWXYZ"
    shades = ["#ff9d00", "#c27800", "#aa6900", "#7a4b00", "#573601", "#422900", "#221000"]

    # Создаем объекты текста один раз
    for i in range(columns):
        x = i * font_size
        start_y = random.randint(-height, 0)
        
        ids = []
        # Создаем голову и хвост
        for j in range(len(shades)):
            txt_id = canvas.create_text(x, start_y - (j * font_size), text=random.choice(chars), 
                                        fill=shades[j], font=("Consolas", font_size))
            ids.append(txt_id)
        
        column_data.append({"y": start_y, "ids": ids})

    def draw():
        for i in range(columns):
            data = column_data[i]
            data["y"] += speed # Плавно увеличиваем Y на пиксели, а не на клетки
            
            x = i * font_size
            
            # Двигаем каждый сегмент хвоста и обновляем символ в "голове"
            for j, txt_id in enumerate(data["ids"]):
                cur_y = data["y"] - (j * font_size)
                canvas.coords(txt_id, x, cur_y)
                
                # Рандомно меняем символ для эффекта мерцания
                if random.random() > 0.9:
                    canvas.itemconfig(txt_id, text=random.choice(chars))
            
            # Если хвост полностью ушел за экран, перекидываем наверх
            if data["y"] - (len(shades) * font_size) > height:
                data["y"] = -font_size
                
        matrix_win.after(20, draw) # Интервал 20мс (~50 FPS)

    matrix_win.bind("<Key>", lambda e: matrix_win.destroy())
    matrix_win.bind("<Button-1>", lambda e: matrix_win.destroy())
    
    draw()

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

# ====== КАСТОМНЫЙ ТИТЛБАР (Верхная поебота с крестиком и тд) ======
def make_titlebar(window, title="Window", close_command=None):
    bg_color = "#1a1a1a"
    accent_color = colors["orange"]

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
    write("ls          - show files and folders in current directory\n")
    write("pwd         - show current directory path\n")
    write("cd <dir>    - change directory\n")
    write("mkdir <n>   - create a new folder\n")
    write("rm <n>      - delete file or folder\n")
    write("clear       - clear terminal screen\n")
    write("file        - open graphical file explorer\n")
    write("open <f>    - open image or video file\n")
    write("nano <f>    - open text editor for a file\n")
    write("unzip <f>   - open or extract ZIP archive\n")
    write("python <f>  - execute a python script\n")
    write("calc        - open BazCalc (calculator)\n")
    write("stat        - open hardware monitor (CPU, GPU, RAM)\n")
    write("taskmgr     - open task manager to manage processes\n")
    write("matrix      - run the digital rain matrix effect\n")
    write("bazfetch    - show system information and BazOS logo\n")
    write("exit        - exit from terminal\n")
    write("help        - show this help message\n")
    write("--------------------------------------------------\n\n")

# ====== ГРАФИЧЕСКАЯ СПРАВКА ======
def graf_help():
    # Создаем окно
    h_win = tk.Toplevel(root)
    h_win.configure(bg="black")
    
    # Используем ваши системные функции для стилизации
    close_cmd = lock_window(h_win, 600, 500)
    make_titlebar(h_win, title="BazOS System Help", close_command=close_cmd)

    # Контейнер для текста с прокруткой
    frame = tk.Frame(h_win, bg="black")
    frame.pack(fill="both", expand=True, padx=15, pady=10)

    scrollbar = tk.Scrollbar(frame, bg="#1a1a1a", troughcolor="black")
    scrollbar.pack(side="right", fill="y")

    help_text = tk.Text(
        frame, bg="black", fg=colors["orange"], 
        font=("Consolas", 11), border=0, 
        yscrollcommand=scrollbar.set, state="normal"
    )
    help_text.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=help_text.yview)

    # Список команд (согласно функционалу вашей ОС)
    commands_info = """
 [ SYSTEM COMMANDS ]
 --------------------------------------------------
 ls        - Show files and folders
 pwd       - Show current directory path
 cd <dir>  - Change directory
 clear     - Clear terminal screen
 exit      - Shutdown system
 bazfetch  - System info & Logo
 help      - Text-based help

 [ FILE MANAGEMENT ]
 --------------------------------------------------
 file      - Open Graphical Explorer
 nano <f>  - Text Editor
 mkdir <n> - Create folder
 rm <n>    - Delete file/folder
 unzip <f> - Archive manager
 open <f>  - Media player (Img/Vid)

 [ APPLICATIONS ]
 --------------------------------------------------
 calc      - Calculator
 stat      - Hardware Monitor
 taskmgr   - Process Manager
 matrix    - Visual Effect
    """
    
    help_text.insert("1.0", commands_info)
    help_text.config(state="disabled") # Только для чтения

    # Подсказка внизу
    footer = tk.Label(h_win, text="Press ESC to close", bg="#1a1a1a", fg=colors["orange"], font=("Consolas", 9))
    footer.pack(fill="x", side="bottom")

def open_calculator():
    calc = tk.Toplevel(root)
    close_cmd = lock_window(calc, 300, 450)
    make_titlebar(calc, title="BazCalc", close_command=close_cmd)
    calc.configure(bg="black")

    display = tk.Entry(calc, bg="#1a1a1a", fg=colors["orange"], font=("Consolas", 20), border=0, justify="right")
    display.pack(fill="x", padx=10, pady=10)

    buttons = [
        '7', '8', '9', '/',
        '4', '5', '6', '*',
        '1', '2', '3', '-',
        'C', '0', '=', '+'
    ]

    btn_frame = tk.Frame(calc, bg="black")
    btn_frame.pack(expand=True, fill="both", padx=5, pady=5)

    def on_click(char):
        if char == '=':
            try: display.insert(tk.END, f"={eval(display.get())}")
            except: display.delete(0, tk.END); display.insert(0, "Error")
        elif char == 'C': display.delete(0, tk.END)
        else: display.insert(tk.END, char)

    for i, btn in enumerate(buttons):
        tk.Button(btn_frame, text=btn, bg="#1a1a1a", fg=colors["orange"], font=("Consolas", 14),
                  activebackground=colors["orange"], border=1, 
                  command=lambda b=btn: on_click(b)).grid(row=i//4, column=i%4, sticky="nsew", padx=2, pady=2)

    for i in range(4):
        btn_frame.grid_columnconfigure(i, weight=1)
        btn_frame.grid_rowconfigure(i, weight=1)

def open_monitor():
    mon = tk.Toplevel(root)
    close_cmd = lock_window(mon, 550, 650)
    make_titlebar(mon, title="BazStat v2.0 - Hardware Pulse", close_command=close_cmd)
    mon.configure(bg="black")

    stats_label = tk.Label(mon, bg="black", fg=colors["orange"], font=("Consolas", 10), justify="left", anchor="nw")
    stats_label.pack(fill="both", expand=True, padx=20, pady=10)

    def update():
        if not mon.winfo_exists(): return
        
        # Данные железа
        cpu_p = psutil.cpu_percent()
        ram = psutil.virtual_memory()
        disk = psutil.disk_usage(current_dir)
        net = psutil.net_io_counters()
        
        # GPU данные через GPUtil
        gpu_text = "No GPU detected or drivers missing"
        try:
            gpus = GPUtil.getGPUs()
            if gpus:
                g = gpus[0]
                gpu_text = f"Name: {g.name}\n Load: {g.load*100:.1f}%\n Temp: {g.temperature}°C\n VRAM: {g.memoryUsed}MB / {g.memoryTotal}MB"
        except: pass

        # Сборка текста
        text = f"--- [ CPU ] ----------------------------\n"
        text += f" Load: {cpu_p}%\n"
        # Температура (может не работать без прав админа)
        try:
            temp = psutil.sensors_temperatures()
            if 'coretemp' in temp:
                text += f" Temp: {temp['coretemp'][0].current}°C\n"
        except: pass
        
        text += f"\n--- [ GPU ] ----------------------------\n{gpu_text}\n"
        
        text += f"\n--- [ MEMORY ] -------------------------\n"
        text += f" Usage: {ram.percent}% ({ram.used//1024**2}MB / {ram.total//1024**2}MB)\n"
        
        text += f"\n--- [ STORAGE ({current_dir[:3]}) ] -----------\n"
        text += f" Usage: {disk.percent}% | Free: {disk.free//1024**3}GB\n"
        
        text += f"\n--- [ NETWORK ] ------------------------\n"
        text += f" Sent: {net.bytes_sent//1024**2} MB\n"
        text += f" Recv: {net.bytes_recv//1024**2} MB\n"

        stats_label.config(text=text)
        mon.after(1000, update)

    update()

def get_system_stats():
    stats = {}
    
    # CPU & RAM
    stats['cpu_load'] = psutil.cpu_percent(interval=None)
    stats['ram'] = psutil.virtual_memory()
    
    # GPU
    gpus = GPUtil.getGPUs()
    if gpus:
        gpu = gpus[0]
        stats['gpu_name'] = gpu.name
        stats['gpu_load'] = gpu.load * 100
        stats['gpu_temp'] = gpu.temperature
        stats['vram_used'] = gpu.memoryUsed
        stats['vram_total'] = gpu.memoryTotal
    else:
        stats['gpu_name'] = "Not Found"
        stats['gpu_load'] = 0
        stats['gpu_temp'] = 0
        
    # Сеть и Диски
    stats['net'] = psutil.net_io_counters()
    stats['disk'] = psutil.disk_usage(current_dir)
    
    return stats

def open_taskmgr():
    tm = tk.Toplevel(root)
    close_cmd = lock_window(tm, 650, 500)
    make_titlebar(tm, title="BazOS Task Manager", close_command=close_cmd)
    tm.configure(bg="black")

    frame = tk.Frame(tm, bg="black")
    frame.pack(fill="both", expand=True, padx=10, pady=5)
    
    scrollbar = tk.Scrollbar(frame, bg="#1a1a1a")
    scrollbar.pack(side="right", fill="y")

    listbox = tk.Listbox(
        frame, bg="black", fg=colors["orange"], 
        font=("Consolas", 10), borderwidth=0, 
        highlightthickness=1, highlightbackground="#333",
        yscrollcommand=scrollbar.set,
        selectbackground=colors["orange"], selectforeground="black"
    )
    listbox.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=listbox.yview)

    def refresh():
        listbox.delete(0, tk.END)
        active_apps = []
        background_procs = []

        for proc in psutil.process_iter(['pid', 'name', 'username']):
            try:
                p_info = proc.info
                # Логика определения: если запущен от текущего юзера - скорее всего активное
                entry_str = f"{p_info['name']:<25} | PID: {p_info['pid']:<8}"
                
                if p_info['username'] == USER:
                    active_apps.append(entry_str)
                else:
                    background_procs.append(entry_str)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        # Сортировка по алфавиту (без учета регистра)
        active_apps.sort(key=str.lower)
        background_procs.sort(key=str.lower)

        listbox.insert(tk.END, " [!] ACTIVE USER APPLICATIONS ".center(60, "-"))
        for app in active_apps:
            listbox.insert(tk.END, f" {app}")
        
        listbox.insert(tk.END, "") 
        listbox.insert(tk.END, " [.] BACKGROUND SYSTEM PROCESSES ".center(60, "-"))
        for proc in background_procs:
            listbox.insert(tk.END, f" {proc}")

    def kill_proc():
        selected = listbox.get(tk.ACTIVE)
        if "PID:" in selected:
            pid = int(selected.split("PID:")[1].strip().split()[0])
            try:
                psutil.Process(pid).kill()
                refresh()
            except Exception as e:
                write(f"taskmgr: failed to kill {pid}: {e}\n")

    btn_frame = tk.Frame(tm, bg="black")
    btn_frame.pack(fill="x", pady=5)
    
    tk.Button(btn_frame, text=" REFRESH ", bg="#1a1a1a", fg=colors["orange"], command=refresh, border=1).pack(side="left", padx=10)
    tk.Button(btn_frame, text=" KILL PROCESS ", bg="#300", fg="#f44", command=kill_proc, border=1).pack(side="right", padx=10)
    
    refresh()

# ====== БЛОКНОТ (nano) ======
def nano(filename, parent_window=None):
    full_path = os.path.join(current_dir, filename)
    editor = tk.Toplevel(root)
    
    # Передаем родителя
    close_cmd = lock_window(editor, 700, 500, parent=parent_window)
    make_titlebar(editor, title=f"nano - {filename}", close_command=close_cmd)
    
    editor.configure(bg="black")
    text_widget = tk.Text(editor, bg="black", fg=colors["orange"], insertbackground=colors["orange"], font=("Consolas", 13), border=0, padx=10, pady=10)
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
    tk.Label(help_bar, text=" [Ctrl+S] Save  [Ctrl+X] Exit ", bg="#1a1a1a", fg=colors["orange"], font=("Consolas", 9)).pack(pady=2)

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

            elif command == "matrix":
                matrix_effect()

            elif command == "unzip":
                if len(parts) > 1:
                    open_archive(parts[1])
                else:
                    write("Usage: unzip <file.zip>\n")

            elif command == "file":
                open_explorer(
                    current_dir,      # start_path
                    root,             # root
                    lock_window,      # lock_window
                    make_titlebar,    # make_titlebar
                    entry,            # entry
                    write,            # write
                    nano,             # nano
                    current_dir,      # current_dir (аргумент пути)
                    open_media,       # open_media
                    open_archive,     # open_archive (ОБЯЗАТЕЛЬНО 10-й аргумент)
                    colors            # colors
                )

            elif command == "calc":
                open_calculator()

            elif command == "stat":
                open_monitor()
                
            elif command == "taskmgr":
                open_taskmgr()

            elif command == "open":
                if len(parts) > 1:
                    open_media(parts[1])
                else:
                    write("open: specify a file\n")

            elif command == "bazfetch":
                bazfetch()

            elif command == "help":
                help()

            elif command == "ghelp": # или "graf_help"
                graf_help()

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
