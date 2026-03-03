from PIL import Image, ImageTk
import tkinter as tk

img = Image.open("img1.jpg")
img.show()

root = tk.Tk()
root.title("Выбор области (ROI)")

canvas = tk.Canvas(root, width=img.size[0], height=img.size[1])
canvas.pack()

# ВАЖНО: используем ImageTk
photo = ImageTk.PhotoImage(img)
canvas.create_image(0, 0, anchor=tk.NW, image=photo)

points = []

def click(event):
    print(f"Клик: x={event.x}, y={event.y}")
    points.append((event.x, event.y))

    if len(points) == 2:
        x1, y1 = points[0]
        x2, y2 = points[1]

        box = (int(x1), int(y1), int(x2), int(y2))
        cropped = img.crop(box)
        cropped.show()
        cropped.save("cropped_roi.jpg")

        print("Фрагмент сохранён как cropped_roi.jpg")
        root.destroy()

canvas.bind("<Button-1>", click)
root.mainloop()