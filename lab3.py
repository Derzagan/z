from PIL import Image
import math

width, height = 500, 500

img = Image.open("img1.jpg")
img2 = Image.new("RGB", (width, height))

center_x, center_y = width // 2, height // 2
max_dist = math.sqrt(center_x**2 + center_y**2)

for x in range(width):
    for y in range(height):
        dist = math.sqrt((x - center_x)**2 + (y - center_y)**2)
        brightness = int(255 * (1 - dist / max_dist))
        brightness = max(0, brightness)  # защита от отрицательных значений
        img.putpixel((x, y), (brightness, 0, 0))

img2.save("radial_gradient.png", "PNG")
img2.show()

# 1 задание
print(img.mode)
# obj = img.load()
# print(obj[25, 45])
# obj[25, 45] = (255, 0, 0)
# img.show()
# print(img.getpixel((25, 45)))
# img.putpixel((25, 45), (255, 0, 0))
# print(img.getpixel((25, 45)))
# img.show()

# 2 задание
# R, G, B = img.split()
# mask = Image.new("L", img.size, 128)
# img2 = Image.merge("RGBA", (R, G, B, mask))
# print(img2.mode)
# img2.show()

# img2 = img.convert("RGBA")
# print(img2.mode)    
# img2.show()
# pil_im = Image.open('img3.jpg').convert('L')
# pil_im.show()

# img = Image.open("img4.jpg")
# print(img.mode)
# img2 = img.convert("P", None, Image.FLOYDSTEINBERG, Image.ADAPTIVE, 128)


# print(img2.mode)
# img2.show()

# 3 задание
# img.save("img5.jpg")
# img.save("img5.bmp", "BMP")

# f = open("img6.bmp", "wb")
# img.save(f, "BMP")
# f.close()

# 4 задание
# img2 = Image.new("RGB", (100, 100))
# img2.show()

# img3 = Image.new("RGB", (100, 100), (255, 0, 0))
# img3.show()

# img4 = Image.new("RGB", (100, 100), "green")
# img4.show()

# img5 = Image.new("RGB", (100, 100), "#f00")
# img5.show()

# img6 = Image.new("RGB", (100, 100), "white")
# img6.show()

# img7 = Image.new("RGB", (320, 240), "silver")
# img7.show()

# img8 = Image.new("RGB", (320, 240), "rgb(205, 100, 200)")
# img8.show()

# img9 = Image.new("RGB", (320, 240), "rgb(10%, 100%, 40%)")
# img9.show()

# img10 = Image.new("RGB", (640, 480), "rgb(205, 100, 200)")
#  img10.show()
# for x in range(640):
#     for y in range(480):
#         img10.putpixel((x, y), (0, 160, 0))
# img10.save("okno.png", "PNG")
# img10.show()

img11 = Image.new("RGB", (640, 480), "rgb(205, 100, 200)")
# img11.show()
for x in range(640):
    for y in range(480):
        img11.putpixel((x, y), (x//3, (x+y)//6, y//3))
img11.save("okno2.png", "PNG")
img11.show()