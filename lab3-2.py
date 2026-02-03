from PIL import Image

width, height = 400, 200
img = Image.new("RGB", (width, height))

color_a = (0, 255, 0)   # зелёный
color_b = (255, 255, 0) # жёлтый

for x in range(width):
    for y in range(height):
        if (x // 20) % 2 == 0:
            img.putpixel((x, y), color_a)
        else:
            img.putpixel((x, y), color_b)

img.save("stripes.png", "PNG")
img.show()
