from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

# img = Image.open("lab4-3.jpg")
# img.show()
# for x in range(img.size[0]):
#     for y in range(img.size[1]):
#         r, g, b = img.getpixel((x, y))
#         img.putpixel((x, y), (b, r, g))
# img.show("lab4-3.jpg")
# img = Image.open("lab4-1.jpg")
#
# r, g, b = img.split()
# img2 = Image.merge("RGB", (r, g, b))
# img2.mode
# img2.show()


im =  Image.open("lab4-6.jpg")
im_arr = np.array(im)


plt.figure()
plt.hist(im_arr.flatten(), 128)
plt.show()
