import pickle
import cv2
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import calibrate
import color_transform
import glob
import matplotlib.cm as cm

def get_perspective_transform_matrix():
    src = np.float32([[625.0,430.0],[501.0,517.0],[793.0,517.0],[655.0,430.0]])
    dst = np.float32([[501.0,0.0],[501.0,517.0],[793.0,517.0],[793.0,0.0]])
    M = cv2.getPerspectiveTransform(src, dst)
    return M;

def warp(img, mtx, dist):
    udst = cv2.undistort(img, mtx, dist, None, mtx)
    cvt = color_transform.combine(udst)
    #cv2.imshow('cvt',cvt)
    M = get_perspective_transform_matrix()
    warped = cv2.warpPerspective(cvt, M, (cvt.shape[1], cvt.shape[0]), flags=cv2.INTER_LINEAR)
    return warped

def write_warped_test_images():

    mtx, dist = calibrate.get_mtx_dist()

    test_images_sl = glob.glob('./test_images/straight_lines*.jpg')
    test_images = glob.glob('./test_images/test*.jpg')

    i = 0
    for test_fname in test_images_sl + test_images:
        i+=1
        img = cv2.imread(test_fname)
        wrp = warp(img, mtx, dist)
        plt.imsave('./output_images/warped' + str(i) + '.png', wrp, cmap=cm.gray)
        #cv2.imwrite('./output_images/warped' + str(i) + '.jpg', wrp)


calibrate.write_undistorted_test_images()
color_transform.write_color_transformed_test_images()
write_warped_test_images()