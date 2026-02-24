from PIL import Image, ImageFilter

img = Image.open("img1.jpg").convert("L")

sobel_x = img.filter(ImageFilter.Kernel(
    (3, 3),
    (-1, 0, 1,
     -2, 0, 2,
     -1, 0, 1),
    1, 0
))

sobel_y = img.filter(ImageFilter.Kernel(
    (3, 3),
    (-1, -2, -1,
      0,  0,  0,
      1,  2,  1),
    1, 0
))

sobel_x.save("sobel_x.jpg")
sobel_y.save("sobel_y.jpg")