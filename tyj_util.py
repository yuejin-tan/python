import cv2
import numpy as np


def myshow(img):
    cv2.namedWindow('tyj_util',cv2.WINDOW_AUTOSIZE)
    cv2.imshow('tyj_util',img)
    while 1:
        if cv2.waitKey(40)&0xff == ord('q'):
            break
    cv2.destroyAllWindows()
