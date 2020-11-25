from typing import Union
from PyQt5.QtGui import QPixmap

MAX_BUFFER_SIZE = 50


class BufferItem:
    data: list = []
    index: int = -1

    def push(self, pixmap: QPixmap):
        if self.index < (len(self.data) - 1):
            del self.data[self.index + 1:]
        new_index = min(self.index + 1, MAX_BUFFER_SIZE)
        if new_index == self.index:
            return
        self.index = new_index
        pm = pixmap.copy()
        self.data.append(pm)
        # print(f'push index: {self.index}, buffer_size: {len(self.data)}')

    def peek(self) -> QPixmap:
        return self.data[self.index].copy()

    def prev(self) -> QPixmap:
        self.index = max(self.index - 1, 0)
        # print(f'back to {self.index}, buffer_size: {len(self.data)}')
        return self.data[self.index].copy()

    def next(self) -> QPixmap:
        self.index = min(self.index + 1, len(self.data) - 1)
        # print(f'forward to {self.index}, buffer_size: {len(self.data)}')
        return self.data[self.index]


class ImageBufferManager:
    pix_buffers: dict = {}
    unsaved_actions: int = 0

    # 更新 Buffer
    def push(self, classname: str, pixmap: QPixmap):
        try:
            curr_buffer: BufferItem = self.pix_buffers[classname]
        except KeyError:
            self.pix_buffers[classname] = BufferItem()
            curr_buffer: BufferItem = self.pix_buffers[classname]

        curr_buffer.push(pixmap)

    # 清空 Buffer
    def renew_buffer(self, init_data: dict = None):
        for buffer in self.pix_buffers.values():
            buffer.data.clear()
        self.pix_buffers.clear()
        if init_data is not None:
            for key, val in init_data.items():
                try:
                    self.pix_buffers[key].push(val)
                except KeyError:
                    self.pix_buffers[key] = BufferItem()
                    self.pix_buffers[key].push(val)
        self.unsaved_actions = 0

    # 復原動作
    def undo_changes(self, _classname: str) -> Union[QPixmap, QPixmap, None]:
        self.unsaved_actions = max(self.unsaved_actions - 1, 0)
        try:
            buffer: BufferItem = self.pix_buffers[_classname]
            return buffer.prev()
        except KeyError:
            return None

    # 重做動作
    def redo_changes(self, _classname: str) -> Union[QPixmap, QPixmap, None]:
        self.unsaved_actions = min(self.unsaved_actions + 1, MAX_BUFFER_SIZE)
        try:
            buffer: BufferItem = self.pix_buffers[_classname]
            return buffer.next()
        except KeyError:
            return None
