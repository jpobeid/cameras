import subprocess
import re

COMMAND_LIST_CAMERAS = 'v4l2-ctl --list-devices'

def get_n_cams():
    cams_process = subprocess.run(COMMAND_LIST_CAMERAS.split(' '), capture_output=True, text=True)
    stdout_list = cams_process.stdout.split('\n')
    # Filter stdout for relevate cams, not BCM ones
    output_list = []
    for i in range(len(stdout_list)):
        line = stdout_list[i]
        if line.startswith('bcm'):
            to_ignore = True
        elif line == '':
            to_ignore = False
        elif not to_ignore:
            output_list.append(line)
    are_cameras_present = len(output_list) != 0
    if are_cameras_present:
        n_cams = sum(list(map(lambda x: not x.startswith('\t'), output_list)))
    else:
        n_cams = 0
    return n_cams
    
