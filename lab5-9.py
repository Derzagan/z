from PIL import Image, ImageFilter, ImageChops

img = Image.open("img3.jpg")

blurred = img.filter(ImageFilter.GaussianBlur(radius=5))

mask = ImageChops.subtract(img, blurred)

sharpened = ImageChops.add(img, mask)

sharpened.show()