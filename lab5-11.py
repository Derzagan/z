import time
from PIL import Image, ImageFilter

img = Image.open("img5.jpg")

# Gaussian radius=2
start = time.time()
img.filter(ImageFilter.GaussianBlur(radius=2))
print("Gaussian r=2:", time.time() - start)

# Gaussian radius=10
start = time.time()
img.filter(ImageFilter.GaussianBlur(radius=10))
print("Gaussian r=10:", time.time() - start)

# Median
start = time.time()
img.filter(ImageFilter.MedianFilter(size=7))
print("Median size=7:", time.time() - start)