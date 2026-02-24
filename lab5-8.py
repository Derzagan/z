import random
from PIL import Image, ImageFilter

img = Image.open("img3.jpg").convert("L")
pixels = img.load()

# Добавление шума "соль и перец"
for i in range(img.width):
    for j in range(img.height):
        rand = random.random()
        if rand < 0.02:
            pixels[i, j] = 0
        elif rand > 0.98:
            pixels[i, j] = 255

img.show()
# BLUR
blur = img.filter(ImageFilter.BoxBlur(2))
blur.show()

# Median
median = img.filter(ImageFilter.MedianFilter(size=3))
median.show()