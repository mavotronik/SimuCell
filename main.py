import gi
import random
import math

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

# Параметры симуляции
WINDOW_SIZE = 1000  # Размер окна
STEP_SIZE = 10  # Дальность шага клетки
REPRODUCTION_INTERVAL = 2000  # Интервал размножения (мс)

class Cell:
    def __init__(self, x=None, y=None):
        self.x = x if x is not None else WINDOW_SIZE / 2
        self.y = y if y is not None else WINDOW_SIZE / 2

    def move(self):
        angle = random.uniform(0, 2 * math.pi)
        self.x += STEP_SIZE * math.cos(angle)
        self.y += STEP_SIZE * math.sin(angle)

        # Ограничение движения внутри окна
        self.x = max(0, min(WINDOW_SIZE, self.x))
        self.y = max(0, min(WINDOW_SIZE, self.y))

    def reproduce(self):
        return Cell(self.x + random.uniform(-5, 5), self.y + random.uniform(-5, 5))

class Simulation(Gtk.Window):
    def __init__(self):
        super().__init__(title="Первичный бульон")
        self.set_default_size(WINDOW_SIZE, WINDOW_SIZE)
        self.connect("destroy", Gtk.main_quit)

        self.cells = [Cell()]  # Одна начальная клетка
        
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_size_request(WINDOW_SIZE, WINDOW_SIZE)
        self.drawing_area.connect("draw", self.on_draw)
        self.add(self.drawing_area)

        # Запуск анимации
        GLib.timeout_add(50, self.update)
        GLib.timeout_add(REPRODUCTION_INTERVAL, self.reproduce_cells)

    def update(self):
        for cell in self.cells:
            cell.move()
        self.drawing_area.queue_draw()  # Перерисовка
        return True

    def reproduce_cells(self):
        if len(self.cells) < 100:  # Ограничение числа клеток
            new_cells = [cell.reproduce() for cell in self.cells if random.random() < 0.3]
            self.cells.extend(new_cells)
        return True

    def on_draw(self, widget, cr):
        # Устанавливаем цвет фона (255, 240, 200)
        cr.set_source_rgb(255/255, 240/255, 200/255)
        cr.paint()

        for cell in self.cells:
            # Рисуем черную окантовку
            cr.set_source_rgb(0, 0, 0)
            cr.arc(cell.x, cell.y, 6, 0, 2 * math.pi)
            cr.stroke_preserve()
            
            # Заполняем цветом фона
            cr.set_source_rgb(255/255, 240/255, 200/255)
            cr.arc(cell.x, cell.y, 6, 0, 2 * math.pi)
            cr.fill()
            
            # Рисуем внутренний круг
            cr.set_source_rgb(0, 0, 0)
            cr.arc(cell.x, cell.y, 3, 0, 2 * math.pi)
            cr.fill()

if __name__ == "__main__":
    win = Simulation()
    win.show_all()
    Gtk.main()
