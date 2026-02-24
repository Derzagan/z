from PIL import Image

img = Image.open("img2.jpg")
img2 = img.resize(( 200, 150) )
img2.size
img.paste((255, 0, 0,), (9, 9, 211, 161) )
img.paste(img2, (10, 10))
img.show()
