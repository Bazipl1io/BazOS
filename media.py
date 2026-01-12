import os
import tkinter as tk
import vlc
from PIL import Image, ImageTk
import __main__ # Импортируем главный модуль для доступа к его функциям

# ====== УНИВЕРСАЛЬНЫЙ МЕДИАПЛЕЕР (ФОТО И ВИДЕО) ======
def open_media(file_path, parent_window=None, root=None, lock_window=None, make_titlebar=None, write=None, current_dir=".", colors=None):
    # Если функции не переданы, берем их из main.py
    root = root or __main__.root
    lock_window = lock_window or __main__.lock_window
    make_titlebar = make_titlebar or __main__.make_titlebar
    write = write or __main__.write
    current_dir = current_dir or __main__.current_dir

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