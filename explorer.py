import os
import tkinter as tk

# ====== ПРОВОДНИК ======
def open_explorer(start_path, root, lock_window, make_titlebar, entry, write, nano, current_dir, open_media):
    path = os.path.abspath(start_path)
    view_mode = "grid"  # Режимы: "grid" или "list"
    sort_mode = "type"

    explorer = tk.Toplevel(root)
    
    def on_explorer_close():
        explorer.destroy()
        entry.focus_force()

    lock_window(explorer, 950, 650)
    # Вынес titlebar в отдельную функцию, чтобы обновлять заголовок
    title_label = make_titlebar(explorer, title=f"Explorer - {path}", close_command=on_explorer_close)
    explorer.configure(bg="#1a1a1a")

    # Панель инструментов
    toolbar = tk.Frame(explorer, bg="#2d2d2d", height=40)
    toolbar.pack(fill="x")
    toolbar.pack_propagate(False)
    
    # Контейнер для контента и скроллбара
    main_container = tk.Frame(explorer, bg="black")
    main_container.pack(fill="both", expand=True)

    # Отдельный блок для скроллбара справа
    scroll_bar_container = tk.Frame(main_container, bg="#111", width=16)
    scroll_bar_container.pack(side="right", fill="y")
    
    scroll_canvas = tk.Canvas(scroll_bar_container, width=12, bg="#111", highlightthickness=0)
    scroll_canvas.pack(fill="y", pady=2)
    scroll_thumb = scroll_canvas.create_rectangle(2, 0, 10, 50, fill="#ff9d00", outline="")

    # Основная область Canvas
    canvas = tk.Canvas(main_container, bg="black", highlightthickness=0)
    canvas.pack(side="left", fill="both", expand=True)
    
    # Фрейм внутри Canvas, где рисуются файлы
    content_frame = tk.Frame(canvas, bg="black")
    canvas.create_window((0, 0), window=content_frame, anchor="nw")

    def update_scroll_thumb(first, last):
        first, last = float(first), float(last)
        c_height = scroll_canvas.winfo_height()
        if c_height <= 1: return
        scroll_canvas.coords(scroll_thumb, 2, first * c_height, 10, last * c_height)

    canvas.configure(yscrollcommand=update_scroll_thumb)

    def scroll_to(event):
        c_height = scroll_canvas.winfo_height()
        pos = event.y / c_height
        canvas.yview_moveto(pos - 0.05)

    scroll_canvas.bind("<B1-Motion>", scroll_to)
    scroll_canvas.bind("<Button-1>", scroll_to)

    def get_file_style(item_path):
        if os.path.isdir(item_path):
            return "📁", "#ff9d00", 0
        ext = os.path.splitext(item_path)[1].lower()
        styles_0 = {
            ".lnk": ("🔅", "#0ec3f0", 4),
            ".url": ("🔅", "#0ec3f0", 4),
        }
        styles_1 = {
            **styles_0,
            ".zip": ("📦", "#f1c40f", 2),
            ".7z": ("📦", "#f1c40f", 2),
            ".jpg": ("🌄", "#a020f0", 3),
            ".jpeg": ("🌄", "#a020f0", 3),
            ".png": ("🌄", "#a020f0", 3),
            ".gif": ("🌄", "#a020f0", 3),
            ".mp3": ("🔊", "#1db954", 3),
            ".mp4": ("📟", "#1db954", 3),
            ".txt": ("📄", "#ffffff", 4),
            ".md":  ("📄", "#ffffff", 4),
            ".py":  ("🐍", "#3776ab", 4),
            ".exe": ("⚙️", "#ff3333", 5),
        }
        return styles_1.get(ext, ("📄", "#bbbbbb", 99))

    def update_view():
        nonlocal path
        for widget in content_frame.winfo_children():
            widget.destroy()
        
        if title_label:
            title_label.config(text=f" 🖥️ Explorer - {path}")

        try:
            items = os.listdir(path)
            if sort_mode == "type":
                items.sort(key=lambda x: (get_file_style(os.path.join(path, x))[2], x.lower()))
            else:
                items.sort(key=lambda x: x.lower())
        except Exception as e:
            items = [f"Error: {e}"]

        if view_mode == "grid":
            render_grid(items)
        else:
            render_list(items)
        
        content_frame.update_idletasks()
        canvas.config(scrollregion=canvas.bbox("all"))

    def render_grid(items):
        col, row = 0, 0
        for item in items:
            full_p = os.path.join(path, item)
            icon, color, _ = get_file_style(full_p)
            card = tk.Frame(content_frame, bg="black", width=120, height=110)
            card.grid(row=row, column=col, padx=5, pady=5)
            card.pack_propagate(False)

            lbl_i = tk.Label(card, text=icon, bg="black", fg=color, font=("Consolas", 30))
            lbl_i.pack()
            lbl_n = tk.Label(card, text=item, bg="black", fg="white", font=("Consolas", 8), wraplength=100)
            lbl_n.pack()

            setup_events(card, [lbl_i, lbl_n], full_p)
            col += 1
            if col > 6: col = 0; row += 1

    def render_list(items):
        for i, item in enumerate(items):
            full_p = os.path.join(path, item)
            icon, color, _ = get_file_style(full_p)
            
            row_frame = tk.Frame(content_frame, bg="black", height=30, width=900)
            row_frame.pack(fill="x", padx=10, pady=1)
            row_frame.pack_propagate(False)

            lbl_i = tk.Label(row_frame, text=icon, bg="black", fg=color, font=("Consolas", 12))
            lbl_i.pack(side="left", padx=5)
            lbl_n = tk.Label(row_frame, text=item, bg="black", fg="white", font=("Consolas", 10))
            lbl_n.pack(side="left", padx=5)

            setup_events(row_frame, [lbl_i, lbl_n], full_p)

    def setup_events(parent, children, full_p):
        def open_ev(e):
            nonlocal path
            if os.path.isdir(full_p):
                path = full_p
                update_view()
            else:
                open_item_logic(full_p)

        for w in [parent] + children:
            w.bind("<Double-Button-1>", open_ev)
            w.bind("<Enter>", lambda e: parent.config(bg="#333"))
            w.bind("<Leave>", lambda e: parent.config(bg="black"))

    def open_item_logic(target_path):
        ext = os.path.splitext(target_path)[1].lower()
        if ext == ".py": 
            write(f"python {target_path}\n")
        elif ext in [".txt", ".md"]: 
            # Добавили parent_window=explorer
            nano(os.path.relpath(target_path, current_dir), parent_window=explorer)
        elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".gif", ".mp4", ".avi", ".mkv", ".mov"]:
            rel_path = os.path.relpath(target_path, current_dir)
            # Добавили parent_window=explorer
            open_media(rel_path, parent_window=explorer) 
        else:
            try: os.startfile(target_path)
            except: pass

    # Кнопки управления
    tk.Button(toolbar, text=" ⬅ Back ", bg="#3d3d3d", fg="white", border=0, 
              command=lambda: go_back_logic()).pack(side="left", padx=5)

    btn_view = tk.Button(toolbar, text=" 🔳 View: Grid ", bg="#3d3d3d", fg="#00ffcc", border=0, 
                        command=lambda: toggle_view_logic())
    btn_view.pack(side="left", padx=5)

    btn_sort = tk.Button(toolbar, text=" 📂 Sort: Type ", bg="#3d3d3d", fg="#ff9d00", border=0, 
                        command=lambda: toggle_sort_logic())
    btn_sort.pack(side="left", padx=5)

    def go_back_logic():
        nonlocal path
        parent = os.path.dirname(path)
        if parent != path:
            path = parent
            update_view()

    def toggle_view_logic():
        nonlocal view_mode
        view_mode = "list" if view_mode == "grid" else "grid"
        btn_view.config(text=f" {'📝' if view_mode == 'list' else '🔳'} View: {view_mode.title()} ")
        update_view()

    def toggle_sort_logic():
        nonlocal sort_mode
        sort_mode = "alpha" if sort_mode == "type" else "type"
        btn_sort.config(text=f" 📂 Sort: {'Type' if sort_mode == 'type' else 'A-Z'} ")
        update_view()

    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    update_view()