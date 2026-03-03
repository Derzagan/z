from PIL import Image, ImageDraw
import tkinter as tk
img = Image.open("img1.jpg")

    # 1. Закраска области (красный прямоугольник)
img1 = img.copy()
img1.paste((255, 0, 0), (0, 0, 100, 100))
img1.show(title="Частичная заливка")

    # 2. Полная заливка (зеленый)
img2 = img.copy()
img2.paste((0, 128, 0), img2.getbbox())
img2.show(title="Полная заливка")
