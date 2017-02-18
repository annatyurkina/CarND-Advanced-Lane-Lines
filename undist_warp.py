import pickle
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import calibrate
import color_transform
import glob
import matplotlib.cm as cm

def get_perspective_transform_matrices():
    src = np.float32([[595.0,450.0],[259.0,687.0],[1056.0,687.0],[687.0,450.0]])
    dst = np.float32([[219.0,0.0],[219.0,720.0],[1091.0,720.0],[1091.0,0.0]])
    M = cv2.getPerspectiveTransform(src, dst)
    Minv = cv2.getPerspectiveTransform(dst, src)
    return M, Minv;

def warp(img, mtx, dist):
    udst = cv2.undistort(img, mtx, dist, None, mtx)
    cvt = color_transform.combine(udst)
    #cv2.imshow('cvt',cvt)
    M, Minv = get_perspective_transform_matrices()
    warped = cv2.warpPerspective(cvt, M, (cvt.shape[1], cvt.shape[0]), flags=cv2.INTER_LINEAR)
    return warped, udst

def write_warped_test_images():

    mtx, dist = calibrate.get_mtx_dist()

    test_images_sl = glob.glob('./test_images/straight_lines*.jpg')
    test_images = glob.glob('./test_images/test*.jpg')

    i = 0
    for test_fname in test_images_sl + test_images:
        i+=1
        img = cv2.imread(test_fname)
        wrp, udst = warp(img, mtx, dist)
        plt.imsave('./output_images/warped' + str(i) + '.png', wrp, cmap=cm.gray)
        #cv2.imwrite('./output_images/warped' + str(i) + '.jpg', wrp)


#calibrate.write_undistorted_test_images()
#color_transform.write_color_transformed_test_images()
#write_warped_test_images()