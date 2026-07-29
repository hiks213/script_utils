import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk


class ImageGridApp:
    def __init__(self, root):
        self.root = root
        self.root.title(
            "PixelGridApp")

        self.file_path = None
        self.original_image = None
        self.scaled_image = None
        self.tk_image = None

        self.img_width = 0
        self.img_height = 0
        self.margin = 30
        self.scale_factor = 1.0

        # --- ИНТЕРФЕЙС: Панель управления ---
        control_frame = tk.Frame(root)
        control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=10)

        btn_load = tk.Button(
            control_frame, text="Загрузить картинку", command=self.load_image)
        btn_load.pack(side=tk.LEFT, padx=5)

        lbl_zoom_info = tk.Label(
            control_frame,
            text="Зум: Ctrl+Колесо | Скролл: Колесо / Shift+Колесо | Сдвиг сетки: Клавиши-Стрелки",
            fg="blue"
        )
        lbl_zoom_info.pack(side=tk.LEFT, padx=10)

        # Выбор Шага
        tk.Label(control_frame, text="Шаг (пикс):").pack(
            side=tk.LEFT, padx=(15, 2))
        self.spin_step = tk.Spinbox(
            control_frame, from_=1, to=200, increment=1, width=5, command=self.on_param_change
        )
        self.spin_step.bind("<Return>", lambda e: self.on_param_change())
        self.spin_step.bind("<FocusOut>", lambda e: self.on_param_change())
        self.spin_step.delete(0, "end")
        self.spin_step.insert(0, "10")
        self.spin_step.pack(side=tk.LEFT, padx=5)

        # Выбор Сдвига X
        tk.Label(control_frame, text="Сдвиг X:").pack(
            side=tk.LEFT, padx=(15, 2))
        self.spin_offset_x = tk.Spinbox(
            control_frame, from_=0, to=10, increment=1, width=5, command=self.trigger_redraw
        )
        self.spin_offset_x.bind("<Return>", lambda e: self.trigger_redraw())
        self.spin_offset_x.bind("<FocusOut>", lambda e: self.trigger_redraw())
        self.spin_offset_x.pack(side=tk.LEFT, padx=5)

        # Выбор Сдвига Y
        tk.Label(control_frame, text="Сдвиг Y:").pack(
            side=tk.LEFT, padx=(15, 2))
        self.spin_offset_y = tk.Spinbox(
            control_frame, from_=0, to=10, increment=1, width=5, command=self.trigger_redraw
        )
        self.spin_offset_y.bind("<Return>", lambda e: self.trigger_redraw())
        self.spin_offset_y.bind("<FocusOut>", lambda e: self.trigger_redraw())
        self.spin_offset_y.pack(side=tk.LEFT, padx=5)

        # Кнопка обработки цвета
        btn_process = tk.Button(
            control_frame, text="Подогнать по цвету", bg="#4CAF50", fg="white",
            font=("Arial", 9, "bold"), command=self.process_cells_color
        )
        btn_process.pack(side=tk.LEFT, padx=15)

        # --- ИНТЕРФЕЙС: Рабочая область со скроллбарами ---
        canvas_frame = tk.Frame(root)
        canvas_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.h_scrollbar = tk.Scrollbar(
            canvas_frame, orient=tk.HORIZONTAL, command=self.on_hscroll)
        self.h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.v_scrollbar = tk.Scrollbar(
            canvas_frame, orient=tk.VERTICAL, command=self.on_vscroll)
        self.v_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas = tk.Canvas(
            canvas_frame, bg="gray",
            xscrollcommand=self.h_scrollbar.set,
            yscrollcommand=self.v_scrollbar.set
        )
        self.canvas.pack(fill=tk.BOTH, expand=True)

        # --- ПРИВЯЗКА СОБЫТИЙ С КЛАВИАТУРЫ И МЫШИ ---
        # Управление сдвигом через клавиши-стрелки
        self.root.bind("<Left>", self.on_arrow_left)
        self.root.bind("<Right>", self.on_arrow_right)
        self.root.bind("<Up>", self.on_arrow_up)
        self.root.bind("<Down>", self.on_arrow_down)

        # Масштабирование (Ctrl + Колесико)
        self.root.bind("<Control-MouseWheel>", self.zoom)
        self.root.bind("<Control-Button-4>", self.zoom_linux)
        self.root.bind("<Control-Button-5>", self.zoom_linux)

        # Вертикальная прокрутка (Колесико мыши)
        self.canvas.bind("<MouseWheel>", self.on_mouse_scroll_v)
        self.canvas.bind("<Button-4>", self.on_mouse_scroll_v_linux)
        self.canvas.bind("<Button-5>", self.on_mouse_scroll_v_linux)

        # Горизонтальная прокрутка (Shift + Колесико мыши)
        self.canvas.bind("<Shift-MouseWheel>", self.on_mouse_scroll_h)
        self.canvas.bind("<Shift-Button-4>", self.on_mouse_scroll_h_linux)
        self.canvas.bind("<Shift-Button-5>", self.on_mouse_scroll_h_linux)

    def load_image(self):
        self.file_path = filedialog.askopenfilename(
            filetypes=[("Изображения", "*.png *.jpg *.jpeg *.bmp *.gif")]
        )
        if self.file_path:
            self.original_image = Image.open(self.file_path).convert("RGB")
            self.scale_factor = 1.0
            self.apply_zoom()

    def apply_zoom(self):
        if not self.original_image:
            return
        orig_w, orig_h = self.original_image.size
        self.img_width = int(orig_w * self.scale_factor)
        self.img_height = int(orig_h * self.scale_factor)

        self.scaled_image = self.original_image.resize(
            (self.img_width, self.img_height), Image.Resampling.NEAREST)
        self.tk_image = ImageTk.PhotoImage(self.scaled_image)

        self.canvas.config(scrollregion=(
            0, 0, self.img_width + self.margin, self.img_height + self.margin))
        self.redraw()

    def zoom(self, event):
        if not self.original_image:
            return
        if event.delta > 0:
            self.scale_factor *= 1.2
        else:
            self.scale_factor /= 1.2
        self.scale_factor = max(0.1, min(self.scale_factor, 30.0))
        self.apply_zoom()

    def zoom_linux(self, event):
        if not self.original_image:
            return
        if event.num == 4:
            self.scale_factor *= 1.2
        elif event.num == 5:
            self.scale_factor /= 1.2
        self.scale_factor = max(0.1, min(self.scale_factor, 30.0))
        self.apply_zoom()

    # --- ОБРАБОТКА НАЖАТИЙ КЛАВИШ-СТРЕЛОК ---
    def change_spinbox_value(self, spinbox, delta):
        """Вспомогательный метод для безопасного изменения значений Spinbox."""
        current_val = self.get_spin_value(spinbox, 0)
        max_val = int(spinbox.cget("to"))
        min_val = int(spinbox.cget("from"))

        new_val = current_val + delta
        if min_val <= new_val <= max_val:
            spinbox.delete(0, "end")
            spinbox.insert(0, str(new_val))
            self.trigger_redraw()

    def on_arrow_left(self, event):
        self.change_spinbox_value(self.spin_offset_x, -1)

    def on_arrow_right(self, event):
        self.change_spinbox_value(self.spin_offset_x, 1)

    def on_arrow_up(self, event):
        self.change_spinbox_value(self.spin_offset_y, -1)

    def on_arrow_down(self, event):
        self.change_spinbox_value(self.spin_offset_y, 1)

    # --- ФУНКЦИИ ПРОКРУТКИ МЫШЬЮ ---
    def on_mouse_scroll_v(self, event):
        if event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        else:
            self.canvas.yview_scroll(1, "units")
        self.redraw_axes()

    def on_mouse_scroll_v_linux(self, event):
        if event.num == 4:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.yview_scroll(1, "units")
        self.redraw_axes()

    def on_mouse_scroll_h(self, event):
        if event.delta > 0:
            self.canvas.xview_scroll(-1, "units")
        else:
            self.canvas.xview_scroll(1, "units")
        self.redraw_axes()

    def on_mouse_scroll_h_linux(self, event):
        if event.num == 4:
            self.canvas.xview_scroll(-1, "units")
        elif event.num == 5:
            self.canvas.xview_scroll(1, "units")
        self.redraw_axes()

    def get_spin_value(self, spinbox, default=0):
        try:
            return int(spinbox.get())
        except ValueError:
            return default

    def on_param_change(self):
        step = self.get_spin_value(self.spin_step, 10)
        if step < 1:
            step = 1
            self.spin_step.delete(0, "end")
            self.spin_step.insert(0, "1")

        self.spin_offset_x.config(to=step)
        self.spin_offset_y.config(to=step)

        if self.get_spin_value(self.spin_offset_x) > step:
            self.spin_offset_x.delete(0, "end")
            self.spin_offset_x.insert(0, str(step))
        if self.get_spin_value(self.spin_offset_y) > step:
            self.spin_offset_y.delete(0, "end")
            self.spin_offset_y.insert(0, str(step))

        self.trigger_redraw()

    def trigger_redraw(self, event=None):
        if self.original_image:
            self.redraw()

    def on_hscroll(self, *args):
        self.canvas.xview(*args)
        self.redraw_axes()

    def on_vscroll(self, *args):
        self.canvas.yview(*args)
        self.redraw_axes()

    def process_cells_color(self):
        if not self.original_image:
            messagebox.showwarning(
                "Внимание", "Сначала загрузите изображение!")
            return

        orig_step = self.get_spin_value(self.spin_step, 10)
        offset_x = self.get_spin_value(self.spin_offset_x, 0)
        offset_y = self.get_spin_value(self.spin_offset_y, 0)

        processed_img = self.original_image.copy()
        pixels = processed_img.load()
        orig_w, orig_h = self.original_image.size

        start_x = (offset_x % orig_step) - orig_step
        start_y = (offset_y % orig_step) - orig_step

        for x in range(start_x, orig_w, orig_step):
            for y in range(start_y, orig_h, orig_step):
                x0, y0 = max(0, x), max(0, y)
                x1, y1 = min(orig_w, x + orig_step), min(orig_h, y + orig_step)

                if x0 >= x1 or y0 >= y1:
                    continue

                # --- Подсчет цветов пикселей внутри текущей ячейки ---
                colors = {}
                for px in range(x0, x1):
                    for py in range(y0, y1):
                        color = pixels[px, py]
                        colors[color] = colors.get(color, 0) + 1

                if not colors:
                    continue

                # Определение доминирующего цвета и заливка ячейки
                dominant_color = max(colors, key=colors.get)
                for px in range(x0, x1):
                    for py in range(y0, y1):
                        pixels[px, py] = dominant_color

        # --- Экспорт обработанного файла в исходную директорию ---
        dir_name, full_file_name = os.path.split(self.file_path)
        file_name, file_ext = os.path.splitext(full_file_name)
        new_file_name = f"{file_name}_ranged{file_ext}"
        save_path = os.path.join(dir_name, new_file_name)

        processed_img.save(save_path)
        self.original_image = processed_img
        self.apply_zoom()

        messagebox.showinfo(
            "Готово", f"Изображение успешно сохранено в:\n{save_path}")

    def redraw(self):
        """Очистка холста и отрисовка сетки поверх картинки."""
        self.canvas.delete("grid_line")
        self.canvas.delete("image")

        self.canvas.create_image(
            self.margin, self.margin,
            image=self.tk_image, anchor=tk.NW, tags="image"
        )

        orig_step = self.get_spin_value(self.spin_step, 10)
        step = int(orig_step * self.scale_factor)
        offset_x = int(self.get_spin_value(
            self.spin_offset_x, 0) * self.scale_factor)
        offset_y = int(self.get_spin_value(
            self.spin_offset_y, 0) * self.scale_factor)

        if step < 1:
            return

        # --- Отрисовка вертикальных линий сетки ---
        start_x = (offset_x % step) - step
        for x in range(start_x, self.img_width + step, step):
            if x >= 0:
                canvas_x = x + self.margin
                self.canvas.create_line(
                    canvas_x, self.margin,
                    canvas_x, self.img_height + self.margin,
                    fill="red", width=1, tags="grid_line"
                )

        # --- Отрисовка горизонтальных линий сетки ---
        start_y = (offset_y % step) - step
        for y in range(start_y, self.img_height + step, step):
            if y >= 0:
                canvas_y = y + self.margin
                self.canvas.create_line(
                    self.margin, canvas_y,
                    self.img_width + self.margin, canvas_y,
                    fill="red", width=1, tags="grid_line"
                )

        self.redraw_axes()

    def redraw_axes(self):
        """Отрисовка осей нумерации, зафиксированных у краев экрана при скролле."""
        self.canvas.delete("axis")

        view_x0 = self.canvas.canvasx(0)
        view_y0 = self.canvas.canvasy(0)
        view_x1 = self.canvas.canvasx(self.canvas.winfo_width())
        view_y1 = self.canvas.canvasy(self.canvas.winfo_height())

        self.canvas.create_rectangle(
            view_x0, view_y0, view_x1, view_y0 + self.margin,
            fill="white", outline="", tags="axis"
        )
        self.canvas.create_rectangle(
            view_x0, view_y0, view_x0 + self.margin, view_y1,
            fill="white", outline="", tags="axis"
        )

        orig_step = self.get_spin_value(self.spin_step, 10)
        step = int(orig_step * self.scale_factor)
        offset_x = int(self.get_spin_value(
            self.spin_offset_x, 0) * self.scale_factor)
        offset_y = int(self.get_spin_value(
            self.spin_offset_y, 0) * self.scale_factor)

        if step < 1:
            return

        # --- Динамический расчет вертикальных номеров ячеек ---
        start_x = (offset_x % step) - step
        base_index_x = - (offset_x // step) - 1 if start_x < 0 else 0
        current_index_x = base_index_x

        for x in range(start_x, self.img_width + step, step):
            if x >= 0:
                canvas_x = x + self.margin
                if current_index_x >= 0 and current_index_x % 5 == 0:
                    text_x = canvas_x + (step / 2)
                    if view_x0 <= text_x <= view_x1 and text_x < self.img_width + self.margin:
                        self.canvas.create_text(
                            text_x, view_y0 + (self.margin / 3),
                            text=str(current_index_x), fill="black",
                            font=("Arial", 9, "bold"), tags="axis"
                        )
                        self.canvas.create_line(
                            text_x, view_y0 + (self.margin * 2 / 3),
                            text_x, view_y0 + self.margin,
                            fill="black", width=1, tags="axis"
                        )
            current_index_x += 1

        # --- Динамический расчет горизонтальных номеров ячеек ---
        start_y = (offset_y % step) - step
        base_index_y = - (offset_y // step) - 1 if start_y < 0 else 0
        current_index_y = base_index_y

        for y in range(start_y, self.img_height + step, step):
            if y >= 0:
                canvas_y = y + self.margin
                if current_index_y >= 0 and current_index_y % 5 == 0:
                    text_y = canvas_y + (step / 2)
                    if view_y0 <= text_y <= view_y1 and text_y < self.img_height + self.margin:
                        self.canvas.create_text(
                            view_x0 + (self.margin / 3), text_y,
                            text=str(current_index_y), fill="black",
                            font=("Arial", 9, "bold"), tags="axis"
                        )
                        self.canvas.create_line(
                            view_x0 + (self.margin * 2 / 3), text_y,
                            view_x0 + self.margin, text_y,
                            fill="black", width=1, tags="axis"
                        )
            current_index_y += 1


# --- Точка входа в программу ---
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("1024x768")
    app = ImageGridApp(root)
    root.mainloop()
