from tkinter import *
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance, ImageDraw
import cv2


open_btn = None
photo = None
canvas = None
frame = None
main_menu = None
current_img = None
open_frame = None
camera_window = None
selected_filter = "all"
pil_img = None
original_img = None

def main():
    global photo, open_btn, canvas, frame, main_menu, open_frame

    root = Tk()
    root.title("Учебная практика")
    root.geometry("400x350")

    main_menu = Menu(root)
    root.config(menu=main_menu)

    file_menu = Menu(main_menu)
    edit_menu = Menu(main_menu)
    view_menu = Menu(main_menu)
    help_menu = Menu(main_menu)
    main_menu.add_cascade(label="Файл", menu=file_menu)
    main_menu.add_cascade(label="Правка", menu=edit_menu, state=DISABLED)
    main_menu.add_cascade(label="Вид", menu=view_menu)
    main_menu.add_cascade(label="Помощь", menu=help_menu)

    file_menu.add_command(label="Открыть", command=open_file)
    file_menu.add_command(label="Сделать снимок с веб-камеры", command=open_camera)
    file_menu.add_command(label="Закрыть", command=close_file)
    file_menu.add_separator()
    file_menu.add_command(label="Выход", command=root.destroy)

    edit_menu.add_command(label="Изменить размер изображения", command=change_size_window)
    edit_menu.add_command(label="Понизить яркость изображения", command=darken_window)
    edit_menu.add_command(label="Нарисовать красный круг", command=draw_circle_window)

    view_menu.add_command(label="Оригинал", command=lambda: filter_select("all"))
    view_menu.add_separator()
    view_menu.add_command(label="Красный канал", command=lambda: filter_select("r"))
    view_menu.add_command(label="Зеленый канал", command=lambda: filter_select("g"))
    view_menu.add_command(label="Синий канал", command=lambda: filter_select("b"))

    help_menu.add_command(
        label="О программе",
        command=lambda: messagebox.showinfo(
            "О программе", 
            "Ознакомительная практика. Вариант 26\n\nЮркевич И.А. ЗКИ25-18Б"
        )
    )

    open_frame = Frame(root)
    open_frame.pack(expand=True)

    open_btn = ttk.Button(open_frame, text="Открыть", command=open_file)
    open_btn.pack()

    frame = Frame(root)
    scroll_y = Scrollbar(frame, orient=VERTICAL)
    scroll_x = Scrollbar(frame, orient=HORIZONTAL)
    canvas = Canvas(
        frame,
        yscrollcommand=scroll_y.set,
        xscrollcommand=scroll_x.set
    )
    scroll_y.config(command=canvas.yview)
    scroll_x.config(command=canvas.xview)

    scroll_y.pack(side=RIGHT, fill=Y)
    scroll_x.pack(side=BOTTOM, fill=X)
    canvas.pack(side=LEFT, fill=BOTH, expand=True)


    root.mainloop()

def open_file():
    global photo, open_frame, canvas, frame, main_menu, current_img, pil_img, original_img

    filepath = filedialog.askopenfilename(filetypes=(("Изображение", "*.png *.jpg"),))
    if filepath != "":
        try:
            original_img = Image.open(filepath)
        except Exception:
            messagebox.showerror("Ошибка открытия", "Не удалось открыть изображение")
            return
        pil_img = show_channel(original_img)
        photo = ImageTk.PhotoImage(pil_img)
        current_img = photo

        open_frame.pack_forget()
        frame.pack(fill=BOTH, expand=True)

        canvas.delete("all")
        canvas.create_image(0, 0, anchor=NW, image=photo)
        canvas.config(scrollregion=(0, 0, pil_img.width, pil_img.height))
        main_menu.entryconfig("Правка", state=NORMAL)

def open_camera():
    global camera_window

    camera = cv2.VideoCapture(0)

    if not camera.isOpened():
        messagebox.showerror(
            "Ошибка камеры",
            "Камера недоступна.\n\n- проверьте подключение камеры\n- разрешите доступ\n- закройте другие приложения, использующие камеру"
        )
        return

    camera_window = Toplevel()
    camera_window.title("Камера")
    camera_window.geometry("800x480")

    camera_label = Label(camera_window)
    camera_label.pack()

    def show_frame():
        if not camera_window.winfo_exists():
            return

        ret, frame_cam = camera.read()

        if ret:
            frame_rgb = cv2.cvtColor(frame_cam, cv2.COLOR_BGR2RGB)

            img = Image.fromarray(frame_rgb)
            img = img.resize((780, 440))

            img_tk = ImageTk.PhotoImage(img)

            camera_label.config(image=img_tk)
            camera_label.image = img_tk

        camera_label.after(30, show_frame)

    def take_photo():
        global photo, current_img, pil_img, open_frame, original_img

        ret, frame_cam = camera.read()

        if ret:
            frame_cam = cv2.cvtColor(frame_cam, cv2.COLOR_BGR2RGB)

            original_img = Image.fromarray(frame_cam)
            pil_img = show_channel(original_img)

            photo = ImageTk.PhotoImage(pil_img)
            current_img = photo

            open_frame.pack_forget()
            frame.pack(fill=BOTH, expand=True)

            canvas.delete("all")
            canvas.create_image(0, 0, anchor=NW, image=photo)

            canvas.config(scrollregion=(0, 0, pil_img.width, pil_img.height))

            main_menu.entryconfig(
                "Правка", state=NORMAL
            )

        camera.release()
        camera_window.destroy()

    ttk.Button(camera_window, text="Сделать снимок", command=take_photo).pack(pady=5)

    show_frame()

    def close_camera():
        camera.release()
        camera_window.destroy()

    camera_window.protocol("WM_DELETE_WINDOW", close_camera)

def close_file():
    global photo, open_btn, canvas, frame, main_menu, current_img, open_frame, original_img, pil_img

    photo = None
    current_img = None
    original_img = None
    pil_img = None
    canvas.delete("all")
    frame.pack_forget()
    open_frame.pack(expand=True)
    open_btn.pack()
    open_frame.update_idletasks()
    main_menu.entryconfig("Правка", state=DISABLED)

def filter_select(channel):
    global selected_filter, original_img

    selected_filter = channel

    if original_img is not None:
        update_canvas(show_channel(original_img))


def show_channel(img):
    global selected_filter

    if img is None:
        return

    img = img.copy()

    if img.mode == "RGBA":
        img = img.convert("RGB")


    if selected_filter == "all":
        return img

    r, g, b = img.split()

    empty = Image.new("L", img.size, 0)

    if selected_filter == "r":
        return Image.merge("RGB", (r, empty, empty))
    elif selected_filter == "g":
        return Image.merge("RGB", (empty, g, empty))
    elif selected_filter == "b":
        return Image.merge("RGB", (empty, empty, b))

def change_size_window():
    win = Toplevel()
    win.title("Измененить размер")
    win.geometry("220x150")
    win.resizable(False, False)

    Label(win, text=f"Текущий размер: {original_img.width}x{original_img.height}").pack(pady=5)

    f = Frame(win)
    f.pack()
    Label(f, text="Ширина:").grid(row=0, column=0, padx=5, pady=5)
    width_entry = Entry(f, width=7)
    width_entry.insert(0, str(original_img.width))
    width_entry.grid(row=0, column=1)

    Label(f, text="Высота:").grid(row=1, column=0, padx=5, pady=5)
    height_entry = Entry(f, width=7)
    height_entry.insert(0, str(original_img.height))
    height_entry.grid(row=1, column=1)

    def apply():
        global original_img
        try:
            w = int(width_entry.get())
            h = int(height_entry.get())
            if w <= 0 or h <= 0 or w >= 15000 or h >= 15000:
                raise ValueError
            original_img = original_img.resize((w, h))
            update_canvas(show_channel(original_img))
            win.destroy()
        except ValueError:
            Label(win, text="Введите целые числа", fg="red").pack()

    ttk.Button(win, text="Применить", command=apply).pack(pady=5)

def darken_window():
    win = Toplevel()
    win.title("Понизить яркость")
    win.geometry("280x140")
    win.resizable(False, False)

    Label(win, text="Множитель яркости:").pack(pady=5)

    slider = Scale(win, from_=0.0, to=1.0, resolution=0.05, orient=HORIZONTAL, length=200)
    slider.set(1.0)
    slider.pack()

    def apply():
        global original_img

        factor = slider.get()
        enhancer = ImageEnhance.Brightness(original_img)
        original_img = enhancer.enhance(factor)
        update_canvas(show_channel(original_img))
        win.destroy()

    ttk.Button(win, text="Применить", command=apply).pack(pady=5)

def draw_circle_window():
    win = Toplevel()
    win.title("Нарисовать красный круг")
    win.geometry("220x150")
    win.resizable(False, False)

    fields = [("X центра:", str(original_img.width // 2)),
              ("Y центра:", str(original_img.height // 2)),
              ("Радиус:",   "50")]
    entries = []

    for label, default in fields:
        f = Frame(win)
        f.pack(fill=X, padx=10, pady=2)
        Label(f, text=label, width=10, anchor=W).pack(side=LEFT)
        e = Entry(f, width=7)
        e.insert(0, default)
        e.pack(side=LEFT)
        entries.append(e)

    def apply():
        global original_img

        try:
            x  = int(entries[0].get())
            y  = int(entries[1].get())
            r  = int(entries[2].get())
            img_copy = original_img.copy()
            draw = ImageDraw.Draw(img_copy)
            draw.ellipse((x - r, y - r, x + r, y + r), outline="red", width=3)
            original_img = img_copy
            update_canvas(show_channel(img_copy))
            win.destroy()
        except ValueError:
            Label(win, text="Введите целые числа", fg="red").pack()

    ttk.Button(win, text="Применить", command=apply).pack(pady=8)

def update_canvas(img):
    global photo, pil_img
    pil_img = img
    photo = ImageTk.PhotoImage(img)
    canvas.delete("all")
    canvas.create_image(0, 0, anchor=NW, image=photo)
    canvas.config(scrollregion=(0, 0, img.width, img.height))

if __name__ == "__main__":
    main()
