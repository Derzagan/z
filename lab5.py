from PIL import Image

img = Image.open('img1.jpg')
img.paste( (255, 0, 0), (0, 0, 100, 100) )
img.show()

mg = Image.open("img1.jpg")
mg.paste( (0, 128, 0), img.getbbox() )
mg.show()