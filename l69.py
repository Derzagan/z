from PIL import Image, ImageDraw
import os

input_folder = "dataset_raw"
output_folder = "dataset_processed"

if not os.path.exists(output_folder):
    os.mkdir(output_folder)

for filename in os.listdir(input_folder):

    file_path = os.path.join(input_folder, filename)

    if filename.lower().endswith((".jpg", ".png", ".jpeg")):

        img = Image.open(file_path)

        # resize 256x256
        img = img.resize((256, 256))

        # grayscale
        img = img.convert("L").convert("RGB")

        # рамка
        draw = ImageDraw.Draw(img)
        draw.rectangle((0, 0, 255, 255), outline="red", width=5)

        # сохранение
        new_name = "proc_" + filename
        save_path = os.path.join(output_folder, new_name)
        img.save(save_path)

        print("Обработан:", filename)

print("Batch обработка завершена")