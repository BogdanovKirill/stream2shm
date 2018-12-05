import cv2
import subprocess as sp
import numpy
import os
import mmap
from time import sleep

FFMPEG_BIN = "./ffmpeg"
INFO_FILE_NAME = '/dev/shm/cam'
IMAGE_FILE_NAME = '/dev/shm/cam_image'
INFO_FILE_SIZE = 4 * 2 + 1

info_fd = os.open(INFO_FILE_NAME, os.O_RDWR | os.O_CREAT);
os.ftruncate(info_fd, INFO_FILE_SIZE);
info_file_map = mmap.mmap(info_fd, INFO_FILE_SIZE)

command = [FFMPEG_BIN, '-y',
        '-rtsp_transport', 'tcp',
        '-i', 'rtsp://admin:123456@192.168.1.77:554/ucast/11',
        '-f', 'stream2shm', INFO_FILE_NAME]

'''command = [FFMPEG_BIN,
        '-hwaccel', 'cuvid',
        '-c:v', 'h264_cuvid',		
        '-rtsp_transport', 'tcp',
        '-i', 'rtsp://admin:123456@192.168.1.77:554/ucast/11',
        '-filter:v', 'hwdownload,format=nv12',
        '-f', 'stream2shm', INFO_FILE_NAME]
'''		
child = sp.Popen(command)

image_width = 0
image_height = 0
frame_array = None

while True:
    if child.poll() is not None:
      break

    refresh_flag = info_file_map[0]

    if refresh_flag:
     new_image_width = int.from_bytes(info_file_map[1:5], byteorder='little', signed=False)
     new_image_height = int.from_bytes(info_file_map[5:9], byteorder='little', signed=False)

     if new_image_width != image_width or new_image_height != image_height:
       image_width = new_image_width
       image_height = new_image_height
       frame_array = numpy.memmap(IMAGE_FILE_NAME, mode="r", dtype="uint8", shape=(image_height,image_width,3))

     cv2.imshow('Video', frame_array)

     if cv2.waitKey(1) & 0xFF == ord('q'):
      break

     info_file_map[0] = 0
     info_file_map.flush(0,1)
    else:
     sleep(0.0166)
	
child.kill()
cv2.destroyAllWindows()
