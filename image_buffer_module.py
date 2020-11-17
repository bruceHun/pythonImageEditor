from PyQt5.QtGui import QPixmap


class ImageBufferModule:
    pix_buffer = []
    buffer_idx: int = -1
    buffer_size: int = 50
    unsaved_actions: int = 0

    # 更新 Buffer
    def update_buffer(self, pixmap: QPixmap):
        # Not at the last element of the buffer
        if self.buffer_idx < (len(self.pix_buffer) - 1):
            del self.pix_buffer[self.buffer_idx + 1:]
            print(f'After clean Buffer Size: {len(self.pix_buffer)}, Current Index: {self.buffer_idx}')
        self.pix_buffer.append(pixmap.copy())
        if len(self.pix_buffer) > self.buffer_size:
            self.pix_buffer.pop(0)
        else:
            self.buffer_idx += 1
        print(f'Buffer Size: {len(self.pix_buffer)}, Current Index: {self.buffer_idx}')

    # 清空 Buffer
    def renew_buffer(self):
        self.pix_buffer.clear()
        self.buffer_idx = 0
        # self.pix_buffer.append(pixmap.copy())
        self.unsaved_actions = 0
        print(f'Buffer Size: {len(self.pix_buffer)}, Current Index: {self.buffer_idx}')

    # 復原動作
    def undo_changes(self):
        new_idx = max(self.buffer_idx - 1, 0)
        if self.buffer_idx == new_idx:
            return None
        else:
            self.buffer_idx = new_idx
        self.unsaved_actions -= 1
        print(f'Undo to Buffer Index: {self.buffer_idx}')
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
