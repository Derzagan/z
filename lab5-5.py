from PIL import Image
from pylab import *
im = array(Image.open("img2.jpg"))
imshow(im)
print("Please click 3 points")
x = ginput(4)
print("you clicked", x)