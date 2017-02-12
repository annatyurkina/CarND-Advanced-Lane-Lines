import numpy as np
import cv2
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.cm as cm
import pickle
import glob
import calibrate

def gray_conversion(iscv2):    
    if(iscv2):
        return cv2.COLOR_BGR2GRAY
    return cv2.COLOR_RGB2GRAY

def hls_conversion(iscv2):    
    if(iscv2):
        return cv2.COLOR_BGR2HLS
    return cv2.COLOR_RGB2HLS

def abs_sobel_thresh(img, orient='x', sobel_kernel=3, thresh=(0, 255), iscv2=True):
    # Grayscale
    gray = cv2.cvtColor(img, gray_conversion(iscv2))
    # Apply cv2.Sobel()
    if(orient == 'x'):
        sobel = cv2.Sobel(gray, cv2.CV_64F, 1, 0)
    else:
        sobel = cv2.Sobel(gray, cv2.CV_64F, 0, 1)
    # Take the absolute value of the output from cv2.Sobel()
    abs_sobel = np.absolute(sobel)
    # Scale the result to an 8-bit range (0-255)
    scaled_sobel = np.uint8(255*abs_sobel/np.max(abs_sobel))
    # Create binary_output and pply lower and upper thresholds
    binary_output= np.zeros_like(scaled_sobel)
    binary_output[(scaled_sobel >= thresh[0]) & (scaled_sobel <= thresh[1])] = 1
    return binary_output

def mag_thresh(img, sobel_kernel=3, mag_thresh=(0, 255), iscv2=True):
    # Convert to grayscale
    gray = cv2.cvtColor(img, gray_conversion(iscv2))
    # Take the gradient in x and y separately
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize = sobel_kernel)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize = sobel_kernel)
    # Calculate the magnitude 
    mag = np.sqrt(sobelx**2 + sobely**2)
    # Scale to 8-bit (0 - 255) and convert to type = np.uint8
    scaled_mag = np.uint8(255*mag/np.max(mag))
    # Create a binary mask where mag thresholds are met
    binary_output = np.zeros_like(scaled_mag)
    binary_output[(scaled_mag >= mag_thresh[0]) & (scaled_mag <= mag_thresh[1])] = 1
    # Return this mask as binary_output image
    return binary_output


def dir_threshold(img, sobel_kernel=3, thresh=(0, np.pi/2), iscv2=True):
    # Convert to grayscale
    gray = cv2.cvtColor(img, gray_conversion(iscv2))
    # Take the gradient in x and y separately
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize = sobel_kernel)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize = sobel_kernel)
    # Take the absolute value of the x and y gradients
    abs_sobelx = np.absolute(sobelx)
    abs_sobely = np.absolute(sobely)
    # Calculate the direction of the gradient 
    dir = np.arctan2(abs_sobely, abs_sobelx)
    # Create a binary mask where direction thresholds are met
    binary_output = np.zeros_like(dir)
    binary_output[(dir >= thresh[0]) & (dir <= thresh[1])] = 1
    # Return this mask as binary_output image
    return binary_output

def hls_select(img, thresh=(0, 255), iscv2=True):
    hls = cv2.cvtColor(img, hls_conversion(iscv2))
    s = hls[:,:,2]
    binary = np.zeros_like(s)
    binary[(s > thresh[0]) & (s <= thresh[1])] = 1
    return binary

def combine(image, ksize=3):
    # Apply each of the thresholding functions
    gradx = abs_sobel_thresh(image, orient='x', sobel_kernel=ksize, thresh=(20, 100))
    grady = abs_sobel_thresh(image, orient='y', sobel_kernel=ksize, thresh=(20, 100))
    mag_binary = mag_thresh(image, sobel_kernel=ksize, mag_thresh=(30, 100))
    dir_binary = dir_threshold(image, sobel_kernel=ksize, thresh=(0.7, 1.3))    
    hls_binary = hls_select(image, thresh=(90, 255))
    # Combine functions in a smart (hopefully) way
    combined = np.zeros_like(dir_binary)
    combined[((gradx == 1) & (hls_binary == 1)) | ((mag_binary == 1) & (dir_binary == 1))] = 1
    return combined

def write_color_transformed_test_images():

    mtx, dist = calibrate.get_mtx_dist()

    test_images_sl = glob.glob('./test_images/straight_lines*.jpg')
    test_images = glob.glob('./test_images/test*.jpg')

    i = 0
    for test_fname in test_images_sl + test_images:
        i+=1
        img = cv2.imread(test_fname)
        dst = cv2.undistort(img, mtx, dist, None, mtx)
        cvt = combine(dst)
        plt.imsave('./output_images/color_transformed' + str(i) + '.png', cvt, cmap=cm.gray)
        #plt.imshow(cvt, cmap='gray')        
        #plt.show()
        #cv2.imwrite('./output_images/color_transformed' + str(i) + '.jpg', cvt)


def compare_transformations():

    mtx, dist = calibrate.get_mtx_dist()

    test_images_sl = glob.glob('./test_images/straight_lines*.jpg')
    test_images = glob.glob('./test_images/test*.jpg')

    for test_fname in test_images_sl + test_images:
        img = cv2.imread(test_fname)
        dst = cv2.undistort(img, mtx, dist, None, mtx)
        # Choose a Sobel kernel size
        ksize = 3 # Choose a larger odd number to smooth gradient measurements

        # Apply each of the thresholding functions
        gradx = abs_sobel_thresh(dst, orient='x', sobel_kernel=ksize, thresh=(20, 100))
        grady = abs_sobel_thresh(dst, orient='y', sobel_kernel=ksize, thresh=(20, 100))
        mag_binary = mag_thresh(dst, sobel_kernel=ksize, mag_thresh=(30, 100))
        dir_binary = dir_threshold(dst, sobel_kernel=ksize, thresh=(0.7, 1.3))    
        hls_binary = hls_select(dst, thresh=(90, 255))

        combined = np.zeros_like(dir_binary)
        combined[((gradx == 1) & (hls_binary == 1)) | ((mag_binary == 1) & (dir_binary == 1))] = 1

        # Plot the result
        f, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3, figsize=(36, 18))
        f.tight_layout()
        ax1.imshow(dst)
        ax1.set_title('Original Image', fontsize=50)
        ax2.imshow(gradx, cmap='gray')
        ax2.set_title('Thresholded Grad. X', fontsize=50)
        ax3.imshow(hls_binary, cmap='gray')
        ax3.set_title('Thresholded Grad. Y', fontsize=50)
        ax4.imshow(mag_binary, cmap='gray')
        ax4.set_title('Thresholded Grad. Mag.', fontsize=50)
        ax5.imshow(dir_binary, cmap='gray')
        ax5.set_title('Thresholded Grad. Dir.', fontsize=50)
        ax6.imshow(combined, cmap='gray')
        ax6.set_title('Combined', fontsize=50)
        plt.subplots_adjust(left=0., right=1, top=0.9, bottom=0.)
        plt.show()


write_color_transformed_test_images()