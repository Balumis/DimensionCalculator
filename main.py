import matplotlib.pyplot as plt
import numpy as np
import matplotlib.image as mpimg
from matplotlib.widgets import Button
from tkinter import Tk, filedialog, simpledialog


class RectangleDrawer:
    def __init__(self, width_mm, height_mm, image_path=None):
        self.width = width_mm
        self.height = height_mm
        self.points = []
        self.image_path = image_path
        self.result_text = None

        # Tworzenie figury i osi z zachowaniem proporcji okna
        self.fig, self.ax = plt.subplots(figsize=(self.width / 100, self.height / 100))
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.set_xticks(np.arange(0, self.width + 1, 10))  # Krok co 10 mm
        self.ax.set_yticks(np.arange(0, self.height + 1, 10))  # Krok co 10 mm
        self.ax.set_aspect('equal')  # Zachowanie proporcji
        self.ax.grid(True)

        # Dodanie tła z obrazkiem, jeśli podano ścieżkę do obrazka
        if self.image_path:
            img = mpimg.imread(self.image_path)
            self.ax.imshow(img, extent=[0, self.width, 0, self.height], alpha=0.3, aspect='auto')

        # Dodanie przycisku resetującego
        reset_ax = self.fig.add_axes(
            [0.8, 0.01, 0.1, 0.05])  # Pozycja przycisku w GUI (lewa, dolna, szerokość, wysokość)
        self.reset_button = Button(reset_ax, 'Reset')
        self.reset_button.on_clicked(self.reset)

        # Dodanie zdarzenia kliknięcia
        self.cid = self.fig.canvas.mpl_connect('button_press_event', self.onclick)

    def onclick(self, event):
        if len(self.points) < 4:  # Możemy wybrać maksymalnie 4 punkty
            ix, iy = event.xdata, event.ydata
            if ix is not None and iy is not None:  # Sprawdzenie, czy kliknięcie było wewnątrz osi
                self.points.append((ix, iy))
                self.ax.plot(ix, iy, 'ro')  # Rysowanie punktu
                self.fig.canvas.draw()
                if len(self.points) == 4:
                    self.draw_lines()

    def draw_lines(self):
        x_coords = [point[0] for point in self.points]
        y_coords = [point[1] for point in self.points]

        # Rysowanie trzech linii łączących cztery punkty w kolejności
        self.ax.plot(x_coords[:2], y_coords[:2], 'b-')  # Linia od 1 do 2
        self.ax.plot(x_coords[1:3], y_coords[1:3], 'b-')  # Linia od 2 do 3
        self.ax.plot(x_coords[2:4], y_coords[2:4], 'b-')  # Linia od 3 do 4

        self.fig.canvas.draw()

        # Obliczanie długości trzech linii
        total_distance = 0
        for i in range(len(self.points) - 1):
            distance = np.sqrt((x_coords[i] - x_coords[i + 1]) ** 2 + (y_coords[i] - y_coords[i + 1]) ** 2)
            total_distance += distance

        # Wyświetlenie wyniku w oknie GUI
        if self.result_text:
            self.result_text.remove()  # Usunięcie poprzedniego tekstu
        self.result_text = self.ax.text(0.5 * self.width, 0.9 * self.height,
                                        f'Całkowita długość trzech linii: {total_distance:.2f} mm',
                                        horizontalalignment='center', verticalalignment='center', fontsize=12,
                                        bbox=dict(facecolor='white', alpha=0.6))

        self.fig.canvas.draw()

    def reset(self, event):
        # Resetowanie rysunku i danych
        self.points = []
        self.ax.cla()  # Czyszczenie osi
        self.ax.set_xlim(0, self.width)
        self.ax.set_ylim(0, self.height)
        self.ax.set_xticks(np.arange(0, self.width + 1, 10))  # Krok co 10 mm
        self.ax.set_yticks(np.arange(0, self.height + 1, 10))  # Krok co 10 mm
        self.ax.set_aspect('equal')  # Zachowanie proporcji
        self.ax.grid(True)

        # Przywrócenie tła z obrazkiem, jeśli podano ścieżkę do obrazka
        if self.image_path:
            img = mpimg.imread(self.image_path)
            self.ax.imshow(img, extent=[0, self.width, 0, self.height], alpha=0.3, aspect='auto')

        self.fig.canvas.draw()

    def show(self):
        plt.show()


def get_rectangle_dimensions():
    root = Tk()
    root.withdraw()  # Ukryj okno główne
    width_mm = simpledialog.askfloat("Input", "Podaj szerokość prostokąta w mm:")
    height_mm = simpledialog.askfloat("Input", "Podaj wysokość prostokąta w mm:")
    return width_mm, height_mm


def get_image_path():
    root = Tk()
    root.withdraw()  # Ukryj okno główne
    file_path = filedialog.askopenfilename(title="Wybierz obrazek",
                                           filetypes=[("Image Files", "*.png;*.jpg;*.jpeg;*.bmp;*.gif")])
    return file_path if file_path else None


# Główna funkcja
def main():
    try:
        # Pobieranie wymiarów od użytkownika
        width_mm, height_mm = get_rectangle_dimensions()

        # Pobieranie ścieżki do obrazka od użytkownika
        image_path = get_image_path()

        # Tworzenie instancji RectangleDrawer
        drawer = RectangleDrawer(width_mm, height_mm, image_path)
        drawer.show()
    except ValueError:
        print("Proszę podać prawidłowe liczby dla wymiarów.")


if __name__ == "__main__":
    main()
