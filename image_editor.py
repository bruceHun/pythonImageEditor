import gc
import os
from tkinter import *
from PIL import ImageTk, Image
import numpy as np

import skimage.io
import skimage.color

from cv2 import circle as cv_circle


class ImageProcessor(object):

    index = 0
    scale = 0.17
    img: np.array = None
    mask: np.array = None
    display_img: np.array = None
    image_list = []
    mask_list = []
    mask_color = (249, 39, 253)
    items = []

    def display_image(self):
        global root
        global render_target

        # render_target.grid_forget()
        # print(mask.shape)
        # print(img.shape)
        height, width = self.mask.shape[:2]

        # print(img[0][0])
        # print(mask[0][0])
        # mask_img = np.where(mask, (0, 0, 0), mask_color).astype(np.uint8)
        blend = np.where(self.mask, self.img, np.maximum(self.mask_color, self.img)).astype(np.uint8)
        # blend = np.maximum(mask_img, img)

        # print(blend[0][0])

        res = Image.fromarray(blend).resize((int(width * self.scale), int(height * self.scale)))
        # print(height * scale, width * scale)
        self.display_img = ImageTk.PhotoImage(res)

        if render_target is None:
            render_target = Canvas(root, width=res.width, height=res.height, bg='gray')
            render_target.grid(row=0, column=0, sticky=N+W+E+S)
            render_target.bind('<Button-1>', self.paint_stroke)

        # Clear Canvas
        render_target.delete(ALL)

        item = render_target.create_image(res.width // 2, res.height // 2, image=self.display_img)
        self.items.append(item)
        # my_label = Label(image=display_img)
        # my_label.grid(row=0, column=0, columnspan=3)
        gc.collect()

    def init(self, image_dir):

        for file in os.listdir(image_dir):
            if file.endswith('.TIF') or file.endswith('.tif'):
                self.image_list.append(image_dir + '/' + file[: len(file) - 9] + '.JPG')
                self.mask_list.append(image_dir + '/' + file)

    def change_image(self, forward: bool):

        if forward:
            self.index = min(self.index + 1, len(self.image_list) - 1)
        else:
            self.index = max(self.index - 1, 0)

        self.img = skimage.io.imread(self.image_list[self.index])
        self.mask = skimage.io.imread(self.mask_list[self.index])

        self.display_image()

    def paint_stroke(self, event):
        cv_circle(self.mask, (int(event.x // self.scale), int(event.y // self.scale)), 100, (255, 255, 255), -1)
        self.display_image()


if __name__ == '__main__':
    import argparse

    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Mask Editor.')
    #
    parser.add_argument('-d', '--directory', required=False,
                        help="Image directory")
    args = parser.parse_args()

    if args.directory is None:
        imgdir = 'images'
    else:
        imgdir = args.directory

    root = Tk()
    root.title('Mask Editor')
    render_target = None

    frame = Frame(root)
    frame.grid(row=1, column=0)

    ip = ImageProcessor()
    # Populate image list and mask list
    ip.init(imgdir)
    ip.change_image(True)

    back_btn = Button(frame, text='<<', command=lambda: ip.change_image(False))
    exit_btn = Button(frame, text='Exit', command=root.quit)
    forward_btn = Button(frame, text='>>', command=lambda: ip.change_image(True))

    back_btn.grid(row=1, column=0)
    exit_btn.grid(row=1, column=1)
    forward_btn.grid(row=1, column=2)

    root.mainloop()


