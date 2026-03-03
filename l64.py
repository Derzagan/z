from PIL import Image, ImageDraw, ImageTk
import tkinter as tk

img = Image.open("img3.jpg")
draw = ImageDraw.Draw(img)

# Точки
draw.ellipse((50, 50, 60, 60), fill="red")
draw.ellipse((100, 100, 110, 110), fill="blue")
draw.ellipse((150, 150, 160, 160), fill="green")

# Линии
draw.line((50, 50, 150, 150), fill="yellow", width=3)
draw.line((150, 150, 300, 100), fill="cyan", width=3)

img.show()