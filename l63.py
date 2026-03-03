from PIL import Image, ImageDraw, ImageTk
import tkinter as tk

img = Image.open("img2.jpg")
img.show()

root = tk.Tk()
root.title("Клики по изображению")

canvas = tk.Canvas(root, width=img.size[0], height=img.size[1])
canvas.pack()

# ВАЖНО: ImageTk.PhotoImage, а не tk.PhotoImage
photo = ImageTk.PhotoImage(img)
canvas.create_image(0, 0, anchor=tk.NW, image=photo)

clicks = []

def click(event):
    print(f"Координаты: x={event.x}, y={event.y}")
    clicks.append((event.x, event.y))
    if len(clicks) == 3:
        print("Три точки:", clicks)

canvas.bind("<Button-1>", click)
root.mainloop()