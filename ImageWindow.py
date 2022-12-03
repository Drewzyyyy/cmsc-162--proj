from tkinter import Toplevel, Label


class ImageWindow(Toplevel):
    def __init__(self, root, images, title="Image", more_info=None):
        Toplevel.__init__(self, root)
        self.title(title)

        if type(images) == list:
            col = 0
            row = 0
            for idx, image in enumerate(images):
                new_image = Label(self,
                                  image=image)
                new_image.image = images
                if col == 3:
                    row += 2
                    col = 0
                new_image.grid(column=col, row=row, sticky='nsew')

                if idx < 8:
                    Label(self, text=f"Bit Plane {idx}").grid(column=col, row=row + 1, sticky='w')
                else:
                    Label(self, text="Watermarked Image").grid(column=col, row=row + 1, sticky='w')
                new_image.grid_propagate(False)
                col += 1
        else:
            image = Label(self,
                          image=images)
            image.image = images
            image.grid(column=0, row=0, sticky='nsew')
            image.grid_propagate(False)

        if more_info is not None:
            Label(self, text=more_info).grid(column=0, row=1)

        self.protocol("WM_DELETE_WINDOW", self.destroy)
