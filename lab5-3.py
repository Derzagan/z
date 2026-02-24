from PIL import Image

img = Image.open("img2.jpg")
white = Image.new("RGB", (img.size[0],100), (255, 255, 255))
mask = Image.new("L", (img.size[0], 100), 64)
img.paste(white, (0, 0), mask)
img.show()