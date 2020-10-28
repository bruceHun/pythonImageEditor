import operator
from PIL import Image
from PIL import ImageDraw

# suppose img1 and img2 are your two images
img1 = Image.new('RGB', size=(100, 100), color=(255, 0, 0))
img2 = Image.new('RGB', size=(120, 130), color=(0, 255, 0))

# suppose img2 is to be shifted by `shift` amount
shift = (50, 60)

# compute the size of the panorama
nw, nh = map(max, map(operator.add, img2.size, shift), img1.size)

# paste img1 on top of img2
newimg1 = Image.new('RGBA', size=(nw, nh), color=(0, 0, 0, 0))
newimg1.paste(img2, shift)
newimg1.paste(img1, (0, 0))

# paste img2 on top of img1
newimg2 = Image.new('RGBA', size=(nw, nh), color=(0, 0, 0, 0))
newimg2.paste(img1, (0, 0))
newimg2.paste(img2, shift)

# blend with alpha=0.5
result = Image.blend(newimg1, newimg2, alpha=0.5)