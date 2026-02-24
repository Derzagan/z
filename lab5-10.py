from PIL import Image, ImageFilter, ImageOps

img = Image.open("img4.jpg").convert("L")

edges = img.filter(ImageFilter.FIND_EDGES)

sketch = ImageOps.invert(edges)

final = sketch.filter(ImageFilter.SMOOTH)

final.show()