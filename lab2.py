from PIL import Image
import io

img = Image.open("img1.jpg")

print(img.size)
print(img.format)
print(img.mode)
print(img.getbbox())
# img.show()
gray = img.convert("L")
# gray.show()

# print(gray.format)
# print(gray.mode)

f = open("img2.gif", "rb")
img = Image.open(f)
# img.show()
# f.close()

f = open("img2.gif", "rb")
data = f.read()
f.close()

img = Image.open(io.BytesIO(data))
# img.show()


try:
    img7 = Image.open("img7.jpg")

    img7.show()
except FileNotFoundError:
    print("File not found")


imgs = ["img3.jpg", "img4.jpg", "img5.jpg"]

for imgD in imgs:
    img = Image.open(imgD)
    print(img.size)
    print(img.format)
    print(img.mode)
    print(img.getbbox())


