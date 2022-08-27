import imp
from multiprocessing.spawn import import_main_path
import tkinter as tk
import numpy as np
from PIL import ImageTk, Image
import cv2

import functions
from gamecube import gc_endpoint, interpret
import gamecube

# First check for cams present
n_cams = functions.get_n_cams()
if n_cams == 0:
    raise ValueError('No cameras detected by system...')
else:
    cams = [cv2.VideoCapture(i) for i in range(0, 2 * n_cams, 2)]
    print(f'Detected {n_cams} camera(s)...')
    print(cams)

# Second check for controller present, and stall till plugged
# ENDPOINT = usb_reader.get_controller_endpoint()

# Tk window
INPUT_LOOP_DELAY = 50

_active_cam = 0

win = tk.Tk()
win.title('Mini app')
win.geometry('600x600')

x, y = 0, 0

def controller_input_loop():
    global x, y, _active_cam

    controller_bytes = gc_endpoint.read(8)[:-1]
    controller_output = gamecube.interpret(controller_bytes)
    signal_A = 'A' in controller_output.get('Main')
    signal_ZR = 'ZR' in controller_output.get('Main')
    signal_ZL = 'ZL' in controller_output.get('Main')

    if signal_ZL:
        _active_cam = (_active_cam + 1) % n_cams
        print(f'Switched to camera {_active_cam}')

    if signal_ZR:
        x, y = 0, 0
    else:
        x_max = (win.winfo_width() - 100) / win.winfo_width()
        y_max = (win.winfo_height() - 100) / win.winfo_height()
        dx, dy = controller_output.get('C-stick')
        x = min(max(0, x + 0.05 * dx), x_max)
        y = min(max(0, y - 0.05 * dy), y_max)
    panel.place(relx=x, rely=y, height=300, width=300)

    if signal_A:
        ok, m_img = cams[_active_cam].read()
        print(ok)
        # BGR to RGB
        m_img = m_img[:, :, ::-1]
        img = Image.fromarray(m_img).resize([300, 300])
        img_tk = ImageTk.PhotoImage(img)
        panel.configure(image=img_tk)
        panel.image = img_tk
    
    win.after(INPUT_LOOP_DELAY, controller_input_loop)

win.after(INPUT_LOOP_DELAY, controller_input_loop)

img_tk = ImageTk.PhotoImage(Image.fromarray((np.random.rand(300, 300) * 256).astype(np.uint8)))
panel = tk.Label(win, image=img_tk)
panel.place(relx=x, rely=y, height=300, width=300)

win.mainloop()