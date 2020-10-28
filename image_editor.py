import gc
import os
from tkinter import *
from PIL import ImageTk, Image
import numpy as np

import skimage.io
import skimage.color


def display_image():
    global my_label
    global img
    global mask
    global display_img
    global mask_color

    my_label.grid_forget()
    # print(mask.shape)
    # print(img.shape)
    height, width = mask.shape[:2]
    scale = 0.17
    # print(img[0][0])
    # print(mask[0][0])
    mask_img = np.where(mask, (0, 0, 0), mask_color).astype(np.uint8)
    # blend = np.where(mask, img, np.maximum(mask_color, img)).astype(np.uint8)
    blend = np.maximum(mask_img, img)

    # print(blend[0][0])

    res = Image.fromarray(blend).resize((int(width * scale), int(height * scale)))
    print(height * scale, width * scale)
    display_img = ImageTk.PhotoImage(res)

    my_label = Label(image=display_img)
    my_label.grid(row=0, column=0, columnspan=3)
    gc.collect()


def init(image_dir):
    global image_list
    global mask_list

    for file in os.listdir(image_dir):
        if file.endswith('.TIF') or file.endswith('.tif'):
            image_list.append(image_dir + '/' + file[: len(file) - 9] + '.JPG')
            mask_list.append(image_dir + '/' + file)


def change_image(forward: bool):
    global im_index
    global image_list
    global mask_list
    global img
    global mask

    if forward:
        im_index = min(im_index + 1, len(image_list) - 1)
    else:
        im_index = max(im_index - 1, 0)

    img = skimage.io.imread(image_list[im_index])
    mask = skimage.io.imread(mask_list[im_index])

    display_image()


root = Tk()
root.title('Mask Editor')

im_index = 0
image_list = []
mask_list = []
mask_color = (249, 39, 253)
# Populate image list and mask list
init('images')
img = skimage.io.imread(image_list[im_index])
mask = skimage.io.imread(mask_list[im_index])

display_img = ImageTk.PhotoImage(Image.fromarray(img))

my_label = Label(image=display_img)
my_label.grid(row=0, column=0, columnspan=3)

display_image()

back_btn = Button(root, text='<<', command=lambda: change_image(False))
exit_btn = Button(root, text='Exit', command=root.quit)
forward_btn = Button(root, text='>>', command=lambda: change_image(True))

back_btn.grid(row=1, column=0)
exit_btn.grid(row=1, column=1)
forward_btn.grid(row=1, column=2)

root.mainloop()


