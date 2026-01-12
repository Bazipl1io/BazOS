import os
import tkinter as tk
import zipfile
import __main__

def open_archive(file_path, parent_window=None, root=None, lock_window=None, make_titlebar=None, write=None, current_dir=".", colors=None):
    # Инициализация системных функций
    root = root or __main__.root
    lock_window = lock_window or __main__.lock_window
    make_titlebar = make_titlebar or __main__.make_titlebar
    write = write or __main__.write
    current_dir = current_dir or __main__.current_dir
    accent = (colors["orange"] if colors else "#ff9d00")

    full_path = os.path.abspath(os.path.join(current_dir, file_path))
    if not os.path.isfile(full_path):
        write(f"archive: {file_path} not found\n")
        return
    
    archive_window = tk.Toplevel(root)
    archive_window.configure(bg="black")
    
    current_zip_path = "" # Путь внутри архива

    close_cmd = lock_window(archive_window, 700, 500, parent=parent_window)
    title_label = make_titlebar(archive_window, title=f"Archive: {os.path.basename(file_path)}", close_command=close_cmd)

    # Панель инструментов (как в WinRAR)
    toolbar = tk.Frame(archive_window, bg="#1a1a1a", height=35)
    toolbar.pack(fill="x")
    
    # Контейнер для списка
    listbox_frame = tk.Frame(archive_window, bg="black")
    listbox_frame.pack(fill="both", expand=True, padx=5, pady=5)

    scrollbar = tk.Scrollbar(listbox_frame, orient="vertical", bg="#1a1a1a", troughcolor="black")
    scrollbar.pack(side="right", fill="y")

    listbox = tk.Listbox(
        listbox_frame, bg="black", fg=accent, font=("Consolas", 11),
        border=0, highlightthickness=0, yscrollcommand=scrollbar.set
    )
    listbox.pack(side="left", fill="both", expand=True)
    scrollbar.config(command=listbox.yview)

    def get_archive_content():
        """Логика навигации внутри ZIP"""
        items = set()
        folders = set()
        
        try:
            with zipfile.ZipFile(full_path, 'r') as z:
                for name in z.namelist():
                    if name.startswith(current_zip_path):
                        relative_name = name[len(current_zip_path):].lstrip('/')
                        if not relative_name: continue
                        
                        parts = relative_name.split('/')
                        if len(parts) > 1: # Это папка
                            folders.add(parts[0])
                        else: # Это файл
                            items.add(parts[0])
        except Exception as e:
            write(f"Archive error: {e}\n")
            return [], []
        
        return sorted(list(folders)), sorted(list(items))

    def update_archive_view():
        listbox.delete(0, tk.END)
        if title_label:
            title_label.config(text=f" Archive: {os.path.basename(file_path)} / {current_zip_path}")
        
        # Кнопка "Назад" внутри архива
        if current_zip_path != "":
            listbox.insert(tk.END, " .. [ Назад ]")
            listbox.itemconfig(tk.END, fg="#0ec3f0")

        folders, files = get_archive_content()
        
        for f in folders:
            listbox.insert(tk.END, f" 📁 {f}/")
            listbox.itemconfig(tk.END, fg=accent)
        
        for f in files:
            listbox.insert(tk.END, f" 📄 {f}")

    def on_double_click(event):
        nonlocal current_zip_path
        selection = listbox.get(listbox.curselection())
        
        if selection == " .. [ Назад ]":
            parts = current_zip_path.rstrip('/').split('/')
            current_zip_path = "/".join(parts[:-1])
            if current_zip_path: current_zip_path += "/"
            update_archive_view()
        elif selection.startswith(" 📁 "):
            folder_name = selection.replace(" 📁 ", "").rstrip('/')
            current_zip_path += folder_name + "/"
            update_archive_view()

    listbox.bind("<Double-Button-1>", on_double_click)

    # Кнопки управления
    btn_frame = tk.Frame(archive_window, bg="#1a1a1a")
    btn_frame.pack(fill="x", side="bottom")

    def extract_all():
        extract_path = os.path.splitext(full_path)[0] + "_extracted"
        try:
            with zipfile.ZipFile(full_path, 'r') as z:
                z.extractall(extract_path)
            write(f"archive: extracted to {extract_path}\n")
            close_cmd()
        except Exception as e:
            write(f"extract error: {e}\n")

    tk.Button(btn_frame, text=" [ EXTRACT ALL ] ", bg="#1a1a1a", fg=accent, 
              font=("Consolas", 10, "bold"), border=0, command=extract_all).pack(side="left", padx=10, pady=5)
    
    update_archive_view()