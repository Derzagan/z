from PIL import Image, ImageDraw

img = Image.open("img1.jpg").convert("RGBA")

# Уменьшенная копия
small = img.copy()
small.thumbnail((200, 200))

# Вставка уменьшенного изображения
img.paste(small, (50, 50))

# Рамка вокруг вставки
draw = ImageDraw.Draw(img)
draw.rectangle(
    (50, 50, 50 + small.size[0], 50 + small.size[1]),
    outline="red",
    width=3
)

# Полупрозрачная белая полоса
overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
overlay_draw = ImageDraw.Draw(overlay)
overlay_draw.rectangle(
    (0, 200, img.size[0], 300),
    fill=(255, 255, 255, 120)
)

img = Image.alpha_composite(img, overlay)

# Вставка повернутого фрагмента
crop = img.crop((100, 100, 300, 300))
crop_rot = crop.rotate(45, expand=True)
img.paste(crop_rot, (300, 50), crop_rot)

img.show()
