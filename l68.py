from PIL import Image, ImageDraw, ImageTk
import tkinter as tk

img = Image.open("img4.jpg")
draw = ImageDraw.Draw(img)

root = tk.Tk()
root.title("Маркеры и сетка")

canvas = tk.Canvas(root, width=img.size[0], height=img.size[1])
canvas.pack()

# ВАЖНО: ImageTk
photo = ImageTk.PhotoImage(img)
canvas.create_image(0, 0, anchor=tk.NW, image=photo)

def click(event):
    x = event.x
    y = event.y

    # Прицел (крестик)
    draw.line((x-40, y, x+40, y), fill="green", width=2)
    draw.line((x, y-40, x, y+40), fill="green", width=2)

    # Сетка (шаг 100px)
    for i in range(0, img.size[0], 100):
        draw.line((i, 0, i, img.size[1]), fill="black", width=1)

    for j in range(0, img.size[1], 100):
        draw.line((0, j, img.size[0], j), fill="black", width=1)

    img.show()
    img.save("markers_grid.jpg")
    print("Сохранено: markers_grid.jpg")
    root.destroy()

canvas.bind("<Button-1>", click)
root.mainloop()