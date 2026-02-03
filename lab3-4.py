from PIL import Image
import os

img = Image.open("nature.jpeg")

img.save("nature.bmp", "BMP")
img.save("nature_rgb.png", "PNG")
img.save("nature.jpg", "JPEG", quality=85)

img_p = img.convert("P", palette=Image.ADAPTIVE, colors=256)
img_p.save("nature_p.png", "PNG")

files = ["nature.bmp", "nature_rgb.png", "nature.jpg", "nature_p.png"]
for f in files:
    size_kb = os.path.getsize(f) // 1024
    print(f"{f}: {size_kb} КБ")
