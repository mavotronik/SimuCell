import gi
import random
import math
import yaml

def load_config(file_path="config.yaml"):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

config = load_config()


gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk, GLib

# Параметры симуляции
WINDOW_SIZE = config["simulation"]["window_size"]  # Размер окна
STEP_SIZE = config["simulation"]["step_size"] # Дальность шага клетки
REPRODUCTION_INTERVAL = config["simulation"]["reproduction_interval"]  # Интервал размножения (мс)

# Класс окружающей среды
class Environment:
    def __init__(self):
        self.temperature = config["environment"]["temperature"]  # в градусах 0 - 45
        self.ph = config["environment"]["ph"] # в единицах pH
        self.o2 = config["environment"]["o2"]  # в процентах 0-100
        self.co2 = config["environment"]["co2"]  # в процентах 0-100
        self.brightness = config["environment"]["brightness"]  # в процентах 0-100

    def fluctuate(self):
        """Небольшие колебания параметров среды со временем."""
        self.temperature += random.uniform(-2.5, 2.5)
        self.ph += random.uniform(-0.1, 0.1)
        self.o2 += random.uniform(-1, 1)
        self.co2 += random.uniform(-1, 1)
        self.brightness += random.uniform(-2, 2)

        self.temperature = max(0, min(45, self.temperature))
        self.ph = max(0, min(14, self.ph))
        self.o2 = max(0, min(100, self.o2))
        self.co2 = max(0, min(100, self.co2))
        self.brightness = max(0, min(100, self.brightness))

# Класс клетки
class Cell:
    def __init__(self, env, x=None, y=None, parent=None):
        self.x = x if x is not None else WINDOW_SIZE / 2
        self.y = y if y is not None else WINDOW_SIZE / 2
        
        if parent:
            # Небольшие мутации параметров от родителя
            self.thermotolerance = parent.thermotolerance + random.uniform(-1, 1)
            self.ph_tolerance = parent.ph_tolerance + random.uniform(-0.2, 0.2)
            self.o2_tolerance = parent.o2_tolerance + random.uniform(-2, 2)
            self.co2_tolerance = parent.co2_tolerance + random.uniform(-2, 2)
            self.brightness_tolerance = parent.brightness_tolerance + random.uniform(-5, 5)
        else:
            # Новая клетка получает параметры среды + небольшое "окно толерантности"
            self.thermotolerance = env.temperature + random.uniform(-5, 5)
            self.ph_tolerance = env.ph + random.uniform(-1, 1)
            self.o2_tolerance = env.o2 + random.uniform(-10, 10)
            self.co2_tolerance = env.co2 + random.uniform(-10, 10)
            self.brightness_tolerance = env.brightness + random.uniform(-20, 20)
        
        self.alive = True

    def move(self):
        angle = random.uniform(0, 2 * math.pi)
        self.x += STEP_SIZE * math.cos(angle)
        self.y += STEP_SIZE * math.sin(angle)

        # Ограничение движения внутри окна
        self.x = max(0, min(WINDOW_SIZE, self.x))
        self.y = max(0, min(WINDOW_SIZE, self.y))

    def check_survival(self, env):
        """Определяет, выживет ли клетка в текущих условиях среды."""
        if (abs(env.temperature - self.thermotolerance) >= 8 or
            abs(env.ph - self.ph_tolerance) >= 2 or
            abs(env.o2 - self.o2_tolerance) >= 20 or
            abs(env.co2 - self.co2_tolerance) >= 15 and
            abs(env.brightness - self.brightness_tolerance) >= 30):
            self.alive = False

    def can_reproduce(self, env):
        """Проверяет, подходят ли условия среды для размножения."""
        return (abs(env.temperature - self.thermotolerance) <= 5 and
                abs(env.ph - self.ph_tolerance) <= 1 and
                abs(env.o2 - self.o2_tolerance) <= 10 and
                abs(env.co2 - self.co2_tolerance) <= 8 and
                abs(env.brightness - self.brightness_tolerance) <= 15)

    def reproduce(self, env):
        """Создает новую клетку с мутациями."""
        return Cell(env, self.x + random.uniform(-5, 5), self.y + random.uniform(-5, 5), parent=self)

# Класс симуляции
class Simulation(Gtk.Window):
    def __init__(self):
        super().__init__(title="Первичный бульон")
        self.set_default_size(WINDOW_SIZE, WINDOW_SIZE)
        self.connect("destroy", Gtk.main_quit)

        self.environment = Environment()
        self.cells = [Cell(self.environment)]  # Одна начальная клетка
        
        self.drawing_area = Gtk.DrawingArea()
        self.drawing_area.set_size_request(WINDOW_SIZE, WINDOW_SIZE)
        self.drawing_area.connect("draw", self.on_draw)
        self.add(self.drawing_area)

        # Запуск анимации
        GLib.timeout_add(50, self.update)
        GLib.timeout_add(REPRODUCTION_INTERVAL, self.reproduce_cells)
        GLib.timeout_add(config["simulation"]["env_update"], self.update_environment)  # Обновление среды

    def update(self):
        for cell in self.cells:
            cell.move()
            cell.check_survival(self.environment)
        self.cells = [cell for cell in self.cells if cell.alive]  # Удаление мертвых
        self.drawing_area.queue_draw()  # Перерисовка
        return True

    def reproduce_cells(self):
        """Размножение клеток при благоприятных условиях."""
        if len(self.cells) < config["simulation"]["max_cells"]:  # Ограничение числа клеток
            new_cells = [cell.reproduce(self.environment) for cell in self.cells 
                         if cell.can_reproduce(self.environment) and random.random() < 0.3]
            self.cells.extend(new_cells)
        return True

    def update_environment(self):
        """Обновление параметров окружающей среды."""
        self.environment.fluctuate()
        return True

    def on_draw(self, widget, cr):
        cr.set_source_rgb(255/255, 240/255, 200/255)
        cr.paint()

        for cell in self.cells:
            cr.set_source_rgb(0, 0, 0)
            cr.arc(cell.x, cell.y, 6, 0, 2 * math.pi)
            cr.stroke_preserve()
            
            cr.set_source_rgb(255/255, 240/255, 200/255)
            cr.arc(cell.x, cell.y, 6, 0, 2 * math.pi)
            cr.fill()
            
            cr.set_source_rgb(0, 0, 0)
            cr.arc(cell.x, cell.y, 3, 0, 2 * math.pi)
            cr.fill()

        # Вывод параметров среды
        cr.set_source_rgb(0, 0, 0)
        cr.move_to(10, 20)
        cr.show_text(f"Temp: {self.environment.temperature:.1f}°C")
        cr.move_to(10, 40)
        cr.show_text(f"pH: {self.environment.ph:.1f}")
        cr.move_to(10, 60)
        cr.show_text(f"O2: {self.environment.o2:.1f}%")
        cr.move_to(10, 80)
        cr.show_text(f"CO2: {self.environment.co2:.1f}%")
        cr.move_to(10, 100)
        cr.show_text(f"Light: {self.environment.brightness:.1f}%")
        cr.move_to(10, 120)
        cr.show_text(f"Cells: {len(self.cells)}")

if __name__ == "__main__":
    win = Simulation()
    win.show_all()
    Gtk.main()
