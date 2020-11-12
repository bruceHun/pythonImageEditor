## Generate python file from Qt Designer
    pyuic5 -x qt_img.ui -o image_editor_qt.py
    
## Default Setting File
#### **`settings.ini`**
```ini
[GeneralSettings]
ImageDir = ./
ZoomScale = 0.06
ZoomMaxScale = 2.0
ZoomMinScale = 0.1

[WorkingState]
Workingimg = 2
Brushsize = 300
Erasemode = 1
```
