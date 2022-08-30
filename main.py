import tkinter as tk
import numpy as np
from PIL import ImageTk, Image
import cv2

import gamecube # This will check for controller and stall
import functions

ON_RPI = True

# Setup GPIO
if ON_RPI:
    import RPi.GPIO as GPIO

    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(37, GPIO.OUT)

# Next check for cams present
n_cams = functions.get_n_cams()
if n_cams == 0:
    raise ValueError('No cameras detected by system...')
else:
    cams = [cv2.VideoCapture(i) for i in range(0, 2 * n_cams, 2)]
    print(f'Detected {n_cams} camera(s)...', cams)

# Tk window
INPUT_LOOP_DELAY = 50
IMAGE_WIDTH = 200
IMAGE_HEIGHT = 200

_active_cam = 0
_can_cam_switch = True

win = tk.Tk()
win.title('Mini app')
win.geometry('600x600')

x, y = 0, 0

def controller_input_loop():
    global x, y, _active_cam, _can_cam_switch

    controller_bytes = gamecube.gc_endpoint.read(8)[:-1]
    controller_output = gamecube.interpret(controller_bytes)
    signal_A = 'A' in controller_output.get('Main')
    signal_B = 'B' in controller_output.get('Main')
    signal_ZR = 'ZR' in controller_output.get('Main')
    signal_ZL = 'ZL' in controller_output.get('Main')
    signal_close = '-' in controller_output.get('Center')

    if ON_RPI:
        if signal_B and GPIO.input(37) == 0:
            GPIO.output(37, True)
            print('37 is on')
        elif not signal_B and GPIO.input(37) == 1:
            GPIO.output(37, False)
            print('37 is off')

    if signal_ZL and _can_cam_switch:
        _active_cam = (_active_cam + 1) % n_cams
        print(f'Switched to camera {_active_cam}')
        _can_cam_switch = False
    elif not signal_ZL:
        _can_cam_switch = True

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
        img = Image.fromarray(m_img).resize([IMAGE_HEIGHT, IMAGE_WIDTH])
        img_tk = ImageTk.PhotoImage(img)
        panel.configure(image=img_tk)
        panel.image = img_tk

    if signal_close:
        print('Closing...')
        if ON_RPI:
            GPIO.cleanup()
        win.destroy()
    
    win.after(INPUT_LOOP_DELAY, controller_input_loop)

win.after(INPUT_LOOP_DELAY, controller_input_loop)

img_tk = ImageTk.PhotoImage(Image.fromarray((np.zeros([IMAGE_HEIGHT, IMAGE_WIDTH]) * 256).astype(np.uint8)))
panel = tk.Label(win, image=img_tk)
panel.place(relx=x, rely=y, height=IMAGE_HEIGHT, width=IMAGE_WIDTH)

win.mainloop()
