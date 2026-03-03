from PIL import Image, ImageDraw

# Основное изображение
img = Image.open("img4.jpg").convert("RGBA")

# Создание логотипа
logo = Image.new("RGBA", (120, 50), (255, 255, 255, 0))
draw = ImageDraw.Draw(logo)
draw.rectangle((0, 0, 120, 50), fill=(0, 0, 0, 120))
draw.text((15, 15), "ISA", fill=(255, 255, 255, 180))

# Размеры
img_w, img_h = img.size
logo_w, logo_h = logo.size

# Координаты
x = img_w - logo_w - 20
y = img_h - logo_h - 20

# Вставка логотипа
img.paste(logo, (x, y), logo)

# УБИРАЕМ ALPHA-КАНАЛ
img = img.convert("RGB")

img.show()
img.save("watermark.jpg")

print("Файл сохранён: watermark.jpg")