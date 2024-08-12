import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog
from PIL import Image, ImageTk
import cv2
import numpy as np


class DimensionCalculatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Dimension Calculator")

        self.image_path = None
        self.image = None
        self.ref_points = []
        self.obj_points = []
        self.ref_real_dimension = None
        self.zoom_factor = 1.0
        self.pan_start_x = 0
        self.pan_start_y = 0

        # Scrollable Canvas
        self.canvas_frame = tk.Frame(root)
        self.canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_frame)
        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.scroll_x = tk.Scrollbar(self.canvas_frame, orient=tk.HORIZONTAL, command=self.canvas.xview)
        self.scroll_x.pack(side=tk.BOTTOM, fill=tk.X)

        self.scroll_y = tk.Scrollbar(self.canvas_frame, orient=tk.VERTICAL, command=self.canvas.yview)
        self.scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(xscrollcommand=self.scroll_x.set, yscrollcommand=self.scroll_y.set)

        # Buttons
        self.load_button = tk.Button(self.root, text="Load Image", command=self.load_image)
        self.load_button.pack(side=tk.LEFT)

        self.measure_ref_button = tk.Button(self.root, text="Measure Reference", command=self.measure_reference)
        self.measure_ref_button.pack(side=tk.LEFT)

        self.measure_obj_button = tk.Button(self.root, text="Measure Object", command=self.measure_object)
        self.measure_obj_button.pack(side=tk.LEFT)

        self.help_button = tk.Button(self.root, text="Help", command=self.show_help)
        self.help_button.pack(side=tk.LEFT)

        self.result_label = tk.Label(self.root, text="")
        self.result_label.pack(side=tk.LEFT)

        # Binding for zooming with mouse wheel
        self.canvas.bind("<MouseWheel>", self.zoom_with_mouse)
        self.canvas.bind("<Button-4>", self.zoom_with_mouse)  # macOS
        self.canvas.bind("<Button-5>", self.zoom_with_mouse)  # macOS

        # Binding for dragging (panning)
        self.canvas.bind("<ButtonPress-2>", self.pan_start)
        self.canvas.bind("<B2-Motion>", self.pan_move)

    def load_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png;*.jpeg;*.pdf")])
        if self.image_path:
            self.image = cv2.imread(self.image_path)
            self.zoom_factor = 1.0
            self.display_image()

    def display_image(self):
        # Apply zoom factor
        image = cv2.resize(self.image, (0, 0), fx=self.zoom_factor, fy=self.zoom_factor)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(image)
        self.tk_image = ImageTk.PhotoImage(image)

        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        self.canvas.config(scrollregion=self.canvas.bbox(tk.ALL))

    def zoom_with_mouse(self, event):
        # Mouse wheel scroll up for zoom in and down for zoom out
        if event.delta > 0 or event.num == 4:  # Mouse wheel up or Button 4 (macOS)
            self.zoom_in()
        elif event.delta < 0 or event.num == 5:  # Mouse wheel down or Button 5 (macOS)
            self.zoom_out()

    def zoom_in(self):
        self.zoom_factor *= 1.1
        self.display_image()

    def zoom_out(self):
        self.zoom_factor /= 1.1
        self.display_image()

    def measure_reference(self):
        self.ref_points = []
        self.canvas.bind("<Button-1>", self.click_event_ref)

    def click_event_ref(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.ref_points.append((x, y))
        self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="red")

        if len(self.ref_points) == 2:
            self.canvas.unbind("<Button-1>")
            self.prompt_ref_dimension()

    def prompt_ref_dimension(self):
        self.ref_real_dimension = float(tk.simpledialog.askstring("Input", "Enter the real dimension between points:"))
        self.draw_line_with_measurement(self.ref_points[0], self.ref_points[1], self.ref_real_dimension, color="red")

    def measure_object(self):
        self.obj_points = []
        self.canvas.bind("<Button-1>", self.click_event_obj)

    def click_event_obj(self, event):
        x, y = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y)
        self.obj_points.append((x, y))
        self.canvas.create_oval(x - 3, y - 3, x + 3, y + 3, fill="blue")

        if len(self.obj_points) == 2:
            self.canvas.unbind("<Button-1>")
            self.calculate_dimension()

    def calculate_dimension(self):
        ref_length_px = np.linalg.norm(np.array(self.ref_points[0]) - np.array(self.ref_points[1]))
        obj_length_px = np.linalg.norm(np.array(self.obj_points[0]) - np.array(self.obj_points[1]))

        scale = self.ref_real_dimension / ref_length_px
        real_obj_length = obj_length_px * scale

        self.result_label.config(text=f"Real Object Dimension: {real_obj_length:.2f} units")
        self.draw_line_with_measurement(self.obj_points[0], self.obj_points[1], real_obj_length, color="blue")

    def draw_line_with_measurement(self, point1, point2, measurement, color="blue"):
        # Draw the line
        self.canvas.create_line(point1, point2, fill=color, width=2)

        # Calculate the midpoint for text placement
        midpoint = ((point1[0] + point2[0]) / 2, (point1[1] + point2[1]) / 2)

        # Draw a rectangle behind the text for better visibility
        bbox = self.canvas.create_text(midpoint, text=f"{measurement:.2f} units", fill=color)
        bbox_coords = self.canvas.bbox(bbox)
        self.canvas.create_rectangle(bbox_coords, fill="white")
        self.canvas.lift(bbox)

    def pan_start(self, event):
        # Capture the starting position of the panning
        self.pan_start_x = event.x
        self.pan_start_y = event.y

    def pan_move(self, event):
        # Calculate the distance moved and scroll the canvas accordingly, with reduced speed
        dx = (event.x - self.pan_start_x) // 2  # Divide by 2 to slow down panning
        dy = (event.y - self.pan_start_y) // 2
        self.canvas.xview_scroll(-dx, "units")
        self.canvas.yview_scroll(-dy, "units")
        self.pan_start_x = event.x
        self.pan_start_y = event.y

    def show_help(self):
        # Ask the user for the preferred language
        language = tk.simpledialog.askstring("Language",
                                             "Choose language / Wybierz język / Wählen Sie eine Sprache (en/pl/de):")

        help_text = {
            "en": ("How to use Dimension Calculator:\n\n"
                   "1. Load an image by clicking 'Load Image'.\n"
                   "2. Use the mouse wheel to zoom in and out.\n"
                   "3. To move the image, press and hold the middle mouse button (or scroll wheel) and drag.\n"
                   "4. Click 'Measure Reference' and select two points on the image to measure the reference dimension. Enter the real dimension.\n"
                   "5. Click 'Measure Object' and select two points to measure the object. The program will calculate the real dimensions based on the reference.\n"
                   "6. The results will be displayed on the image and below.\n"
                   "\nMake sure the image is fully loaded and fits within the canvas."),
            "pl": ("Jak korzystać z Dimension Calculator:\n\n"
                   "1. Załaduj obraz, klikając 'Load Image'.\n"
                   "2. Użyj kółka myszy, aby powiększać i pomniejszać obraz.\n"
                   "3. Aby przesunąć obraz, naciśnij i przytrzymaj środkowy przycisk myszy (lub kółko przewijania) i przeciągnij.\n"
                   "4. Kliknij 'Measure Reference' i wybierz dwa punkty na obrazie, aby zmierzyć wymiary referencyjne. Wprowadź rzeczywisty wymiar.\n"
                   "5. Kliknij 'Measure Object' i wybierz dwa punkty, aby zmierzyć obiekt. Program obliczy rzeczywiste wymiary na podstawie referencji.\n"
                   "6. Wyniki zostaną wyświetlone na obrazie i poniżej.\n"
                   "\nUpewnij się, że obraz jest w pełni załadowany i mieści się w oknie."),
            "de": ("So verwenden Sie den Dimension Calculator:\n\n"
                   "1. Laden Sie ein Bild, indem Sie auf 'Load Image' klicken.\n"
                   "2. Verwenden Sie das Mausrad, um das Bild zu vergrößern und zu verkleinern.\n"
                   "3. Um das Bild zu verschieben, drücken und halten Sie die mittlere Maustaste (oder das Scrollrad) und ziehen Sie.\n"
                   "4. Klicken Sie auf 'Measure Reference' und wählen Sie zwei Punkte auf dem Bild aus, um die Referenzdimension zu messen. Geben Sie die tatsächliche Dimension ein.\n"
                   "5. Klicken Sie auf 'Measure Object' und wählen Sie zwei Punkte aus, um das Objekt zu messen. Das Programm berechnet die tatsächlichen Dimensionen basierend auf der Referenz.\n"
                   "6. Die Ergebnisse werden auf dem Bild und unten angezeigt.\n"
                   "\nStellen Sie sicher, dass das Bild vollständig geladen ist und in das Fenster passt.")
        }

        if language in help_text:
            messagebox.showinfo("Help", help_text[language])
        else:
            messagebox.showinfo("Help", help_text["en"])  # Default to English if no valid language is chosen


def main():
    root = tk.Tk()
    app = DimensionCalculatorApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
