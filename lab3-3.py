import os
from PIL import Image

input_dir = "input_images"
output_dir = "output_images"

os.makedirs(output_dir, exist_ok=True)

for filename in os.listdir(input_dir):
    if filename.lower().endswith(".jpg"):
        img = Image.open(os.path.join(input_dir, filename))

        img_p = img.convert(
            "P",
            palette=Image.ADAPTIVE,
            colors=256,
            dither=Image.FLOYDSTEINBERG
        )

        new_name = "web_" + filename.replace(".jpg", ".png")
        img_p.save(os.path.join(output_dir, new_name))

        print(f"Обработан файл: {filename}")
