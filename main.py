import tkinter as tk
import os
import shutil
import getpass
import platform
import subprocess
import psutil
import wmi
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

def on_closing():
    if os.path.exists(history_file):
        os.remove(history_file)
    root.destroy()

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


# ====== ПРОВОДНИК ======
def open_explorer(start_path):
    path = start_path
    explorer = tk.Toplevel(root)
    explorer.title(f"Explorer - {path}")
    explorer.geometry("600x400")
    explorer.configure(bg="#1a1a1a")

    path_label = tk.Label(explorer, text=path, bg="#1a1a1a", fg="#ff9d00", font=("Consolas", 12))
    path_label.pack(anchor="w", padx=5, pady=5)

    def go_back():
        nonlocal path
        parent = os.path.dirname(path)
        if os.path.exists(parent):
            path = parent
            update_list(path)

    btn_frame = tk.Frame(explorer, bg="#1a1a1a")
    btn_frame.pack(fill="x", padx=5)

    back_btn = tk.Button(
        btn_frame,
        text=".. (Back)",
        bg="#2d2929",
        fg="#ff9d00",
        font=("Consolas", 10),
        border=0,
        command=go_back
    )
    back_btn.pack(anchor="w")

    listbox = tk.Listbox(explorer, bg="black", fg="#ff9d00", font=("Consolas", 12))
    listbox.pack(fill="both", expand=True)

    def update_list(dir_path):
        listbox.delete(0, tk.END)
        path_label.config(text=dir_path)
        try:
            for item in os.listdir(dir_path):
                listbox.insert(tk.END, item)
        except Exception as e:
            listbox.insert(tk.END, f"Error: {e}")

    def on_double_click(event):
        nonlocal path
        selection = listbox.curselection()
        if not selection:
            return

        selected = listbox.get(selection[0])
        full_path = os.path.join(path, selected)

        # Если папка — заходим в неё
        if os.path.isdir(full_path):
            path = full_path
            update_list(path)
            return

        # Если файл
        ext = os.path.splitext(selected)[1].lower()

        # Текстовые файлы → nano
        if ext in [".txt", ".py", ".md", ".json", ".cfg", ".ini", ".log"]:
            nano(os.path.relpath(full_path, current_dir))

        # Картинки → твой просмотрщик
        elif ext in [".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp"]:
            open_image(os.path.relpath(full_path, current_dir))

        # Всё остальное → через Windows
        else:
            try:
                os.startfile(full_path)
            except Exception as e:
                write(f"open: cannot open file: {e}\n")


    listbox.bind("<Double-Button-1>", on_double_click)
    update_list(path)

# ====== БЛОКНОТ (nano) ======
def nano(filename):
    full_path = os.path.join(current_dir, filename)

    editor = tk.Toplevel(root)
    editor.title(f"nano - {filename}")
    editor.geometry("700x500")
    editor.configure(bg="black")

    text = tk.Text(
        editor,
        bg="#1a1a1a",
        fg="#ff9d00",
        insertbackground="#ff9d00",
        font=("Consolas", 14)
    )
    text.pack(expand=True, fill="both")

    # Если файл существует — загрузить его
    if os.path.exists(full_path):
        try:
            with open(full_path, "r", encoding="utf-8") as f:
                text.insert("1.0", f.read())
        except Exception as e:
            write(f"nano: error opening file: {e}\n")

    # Сохранение
    def save_file(event=None):
        try:
            with open(full_path, "w", encoding="utf-8") as f:
                f.write(text.get("1.0", "end-1c"))
            write(f"nano: saved {filename}\n")
        except Exception as e:
            write(f"nano: error saving file: {e}\n")
        return "break"

    # Закрытие
    def exit_editor(event=None):
        editor.destroy()
        return "break"

    editor.bind("<Control-s>", save_file)
    editor.bind("<Control-x>", exit_editor)

    info = tk.Label(
        editor,
        text="Ctrl+S — сохранить | Ctrl+X — выйти",
        bg="#111",
        fg="#ff9d00",
        font=("Consolas", 12)
    )
    info.pack(fill="x")


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


# ====== ПРОСМОТРЩИК КАРТИНОК ======
def open_image(file_path):
    full_path = os.path.join(current_dir, file_path)
    if not os.path.isfile(full_path):
        write(f"open: {file_path} does not exist\n")
        return

    try:
        img = Image.open(full_path)
        img_width, img_height = img.size

        img_window = tk.Toplevel(root)
        img_window.title(file_path)
        img_window.configure(bg="black")

        canvas = tk.Canvas(img_window, bg="black", highlightthickness=0)
        canvas.pack(fill="both", expand=True)

        def resize_image(event):
            new_width = event.width
            new_height = event.height
            ratio = min(new_width / img_width, new_height / img_height)
            display_width = int(img_width * ratio)
            display_height = int(img_height * ratio)

            resized = img.resize((display_width, display_height), Image.LANCZOS)
            photo_resized = ImageTk.PhotoImage(resized)

            canvas.delete("all")
            canvas.create_image(
                (new_width - display_width)//2,
                (new_height - display_height)//2,
                anchor="nw",
                image=photo_resized
            )
            canvas.image = photo_resized

        canvas.bind("<Configure>", resize_image)
        img_window.minsize(200, 200)

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
                open_explorer(current_dir)

            elif command == "open":
                if len(parts) > 1:
                    open_image(parts[1])
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
