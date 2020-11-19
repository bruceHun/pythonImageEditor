from PyQt5.QtGui import QPixmap


class BufferItem:
    c_name: str = ''
    data: QPixmap = None

    def __init__(self, Name: str, data: QPixmap):
        self.c_name = Name
        self.data = data.copy()


class ImageBufferModule:
    pix_buffer = []
    buffer_begin: int = 0
    buffer_idx: int = -1
    buffer_size: int = 50
    unsaved_actions: int = 0

    # 更新 Buffer
    def push(self, classname: str, pixmap: QPixmap):
        # Not at the last element of the buffer
        if self.buffer_idx < (len(self.pix_buffer) - self.buffer_begin - 1):
            del self.pix_buffer[self.buffer_idx + 1:]
            print(f'After clean Buffer Size: {len(self.pix_buffer)}, Current Index: {self.buffer_idx}')
        new_item = BufferItem(classname, pixmap)
        self.pix_buffer.append(new_item)
        if len(self.pix_buffer) > self.buffer_size:
            self.pix_buffer.pop(0)
        else:
            self.buffer_idx += 1
        print(f'Buffer Size: {len(self.pix_buffer)}, Current Index: {self.buffer_idx}, class: {classname}')

    # 清空 Buffer
    def renew_buffer(self, init_data: dict = None):
        self.pix_buffer.clear()
        if init_data is not None:
            for key, val in init_data.items():
                item = BufferItem(key, val)
                self.pix_buffer.append(item)
        self.buffer_idx = len(self.pix_buffer) - 1
        self.buffer_begin = self.buffer_idx
        self.unsaved_actions = 0
        print(f'Buffer Size: {len(self.pix_buffer)}, Current Index: {self.buffer_idx}, begin: {self.buffer_begin}')

    # 復原動作
    def undo_changes(self):
        new_idx = max(self.buffer_idx - 1, 0)
        if self.buffer_idx == new_idx:
            return None
        else:
            self.buffer_idx = new_idx
        self.unsaved_actions -= 1

        return self.pix_buffer[self.buffer_idx]

    # 重做動作
    def redo_changes(self):
        new_idx = min(self.buffer_idx + 1, len(self.pix_buffer) - 1)
        if self.buffer_idx == new_idx:
            return None
        else:
            self.buffer_idx = new_idx
        self.unsaved_actions += 1
        print(f'Redo to Buffer Index: {self.buffer_idx}')
        return self.pix_buffer[self.buffer_idx]
