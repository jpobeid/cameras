import subprocess
import re

COMMAND_LIST_CAMERAS = 'v4l2-ctl --list-devices'

def get_n_cams():
    cams_process = subprocess.run(COMMAND_LIST_CAMERAS.split(' '), capture_output=True, text=True)
    are_cameras_present = cams_process.stdout != ''
    if are_cameras_present:
        mounted_videos = re.findall(r'video\d', cams_process.stdout)
        n_cams = len(mounted_videos) // 2
    else:
        n_cams = 0
    return n_cams