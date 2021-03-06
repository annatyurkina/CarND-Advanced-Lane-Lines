import numpy as np
import cv2
import matplotlib.pyplot as plt
import calibrate
import glob
import undist_warp
import math
from moviepy.editor import VideoFileClip
import line
import matplotlib.cm as cm

LEFT_LINE = line.Line()
RIGHT_LINE = line.Line()

def fit(binary_warped, undistorted_color, verbose = False, test_mode = False):
    if(verbose):
        plt.imshow(binary_warped)
        plt.show()

    # Identify the x and y positions of all nonzero pixels in the image
    nonzero = binary_warped.nonzero()
    nonzeroy = np.array(nonzero[0])
    nonzerox = np.array(nonzero[1])
    # Set the width of the windows +/- margin
    margin = 100
    # Create an output image to draw on and  visualize the result
    out_img = np.dstack((binary_warped, binary_warped, binary_warped))*255
    
    if(LEFT_LINE.detected == False):
        # Take a histogram of the bottom half of the image
        histogram = np.sum(binary_warped[math.floor(binary_warped.shape[0]/2):,:], axis=0)
        # Find the peak of the left and right halves of the histogram
        # These will be the starting point for the left and right lines
        midpoint = np.int(histogram.shape[0]/2)
        leftx_base = np.argmax(histogram[:midpoint])
        rightx_base = np.argmax(histogram[midpoint:]) + midpoint

        # Choose the number of sliding windows
        nwindows = 9
        # Set height of windows
        window_height = np.int(binary_warped.shape[0]/nwindows)
        # Current positions to be updated for each window
        leftx_current = leftx_base
        rightx_current = rightx_base
        # Set minimum number of pixels found to recenter window
        minpix = 50
        # Create empty lists to receive left and right lane pixel indices
        left_lane_inds = []
        right_lane_inds = []

        # Step through the windows one by one
        for window in range(nwindows):
            # Identify window boundaries in x and y (and right and left)
            win_y_low = binary_warped.shape[0] - (window+1)*window_height
            win_y_high = binary_warped.shape[0] - window*window_height
            win_xleft_low = leftx_current - margin
            win_xleft_high = leftx_current + margin
            win_xright_low = rightx_current - margin
            win_xright_high = rightx_current + margin
            # Draw the windows on the visualization image
            cv2.rectangle(out_img,(win_xleft_low,win_y_low),(win_xleft_high,win_y_high),(0,255,0), 2) 
            cv2.rectangle(out_img,(win_xright_low,win_y_low),(win_xright_high,win_y_high),(0,255,0), 2) 
            # Identify the nonzero pixels in x and y within the window
            good_left_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_xleft_low) & (nonzerox < win_xleft_high)).nonzero()[0]
            good_right_inds = ((nonzeroy >= win_y_low) & (nonzeroy < win_y_high) & (nonzerox >= win_xright_low) & (nonzerox < win_xright_high)).nonzero()[0]
            # Append these indices to the lists
            left_lane_inds.append(good_left_inds)
            right_lane_inds.append(good_right_inds)
            # If you found > minpix pixels, recenter next window on their mean position
            if len(good_left_inds) > minpix:
                leftx_current = np.int(np.mean(nonzerox[good_left_inds]))
            if len(good_right_inds) > minpix:        
                rightx_current = np.int(np.mean(nonzerox[good_right_inds]))

        # Concatenate the arrays of indices
        left_lane_inds = np.concatenate(left_lane_inds)
        right_lane_inds = np.concatenate(right_lane_inds)
        print('not_detected')

    else:
        # use areas around last fitted lines to find line pixels
        left_lane_inds = ((nonzerox > (LEFT_LINE.current_fit[0]*(nonzeroy**2) + LEFT_LINE.current_fit[1]*nonzeroy + LEFT_LINE.current_fit[2] - margin)) & (nonzerox < (LEFT_LINE.current_fit[0]*(nonzeroy**2) + LEFT_LINE.current_fit[1]*nonzeroy + LEFT_LINE.current_fit[2] + margin))) 
        right_lane_inds = ((nonzerox > (RIGHT_LINE.current_fit[0]*(nonzeroy**2) + RIGHT_LINE.current_fit[1]*nonzeroy + RIGHT_LINE.current_fit[2] - margin)) & (nonzerox < (RIGHT_LINE.current_fit[0]*(nonzeroy**2) + RIGHT_LINE.current_fit[1]*nonzeroy + RIGHT_LINE.current_fit[2] + margin))) 
        print('detected')

    # Extract left and right line pixel positions
    leftx = nonzerox[left_lane_inds]
    lefty = nonzeroy[left_lane_inds] 
    rightx = nonzerox[right_lane_inds]
    righty = nonzeroy[right_lane_inds] 

    # Fit a second order polynomial to each
    left_fit = np.polyfit(lefty, leftx, 2)
    right_fit = np.polyfit(righty, rightx, 2)

    # Generate x and y values for plotting
    ploty = np.linspace(0, binary_warped.shape[0]-1, binary_warped.shape[0] )
    left_fitx = left_fit[0]*ploty**2 + left_fit[1]*ploty + left_fit[2]
    right_fitx = right_fit[0]*ploty**2 + right_fit[1]*ploty + right_fit[2]

    out_img[nonzeroy[left_lane_inds], nonzerox[left_lane_inds]] = [255, 0, 0]
    out_img[nonzeroy[right_lane_inds], nonzerox[right_lane_inds]] = [0, 0, 255]
    if(verbose):
        plt.imshow(out_img)
        plt.plot(left_fitx, ploty, color='yellow')
        plt.plot(right_fitx, ploty, color='yellow')
        plt.xlim(0, 1280)
        plt.ylim(720, 0)
        plt.show()

    y_eval = np.max(ploty)
    left_curverad = ((1 + (2*left_fit[0]*y_eval + left_fit[1])**2)**1.5) / np.absolute(2*left_fit[0])
    right_curverad = ((1 + (2*right_fit[0]*y_eval + right_fit[1])**2)**1.5) / np.absolute(2*right_fit[0])

    LEFT_LINE.was_detected(left_fitx, left_curverad, left_fit, right_curverad, right_fit, test_mode = test_mode)
    RIGHT_LINE.was_detected(right_fitx, right_curverad, right_fit, left_curverad, left_fit, not LEFT_LINE.detected, test_mode = test_mode)

    # Define conversions in x and y from pixels space to meters
    ym_per_pix = 30/720 # meters per pixel in y dimension
    xm_per_pix = 3.7/700 # meters per pixel in x dimension

    # Fit new polynomials to x,y in world space
    left_fit_cr = np.polyfit(lefty*ym_per_pix, leftx*xm_per_pix, 2)
    right_fit_cr = np.polyfit(righty*ym_per_pix, rightx*xm_per_pix, 2)
    # Calculate the new radii of curvature
    left_curverad = ((1 + (2*left_fit_cr[0]*y_eval*ym_per_pix + left_fit_cr[1])**2)**1.5) / np.absolute(2*left_fit_cr[0])
    right_curverad = ((1 + (2*right_fit_cr[0]*y_eval*ym_per_pix + right_fit_cr[1])**2)**1.5) / np.absolute(2*right_fit_cr[0])
    # Now our radius of curvature is in meters
    if(verbose):
        print(left_curverad, 'm', right_curverad, 'm')
    # Example values: 632.1 m    626.2 m

    # car offset from center
    car_offset = ((left_fit[2] + right_fit[2]) / 2.0 - binary_warped.shape[0] / 2.0) * xm_per_pix
    if(verbose):
        print('car offset: ', car_offset)

    LEFT_LINE.set_output_params(left_curverad, car_offset)
    RIGHT_LINE.set_output_params(right_curverad, car_offset)

    # Create an image to draw the lines on
    warp_zero = np.zeros_like(binary_warped).astype(np.uint8)
    color_warp = np.dstack((warp_zero, warp_zero, warp_zero))

    # Recast the x and y points into usable format for cv2.fillPoly()
    left_avg_fitx = LEFT_LINE.best_fit[0]*ploty**2 + LEFT_LINE.best_fit[1]*ploty + LEFT_LINE.best_fit[2]
    right_avg_fitx = RIGHT_LINE.best_fit[0]*ploty**2 + RIGHT_LINE.best_fit[1]*ploty + RIGHT_LINE.best_fit[2]
    pts_left = np.array([np.transpose(np.vstack([left_avg_fitx, ploty]))])
    pts_right = np.array([np.flipud(np.transpose(np.vstack([right_avg_fitx, ploty])))])
    pts = np.hstack((pts_left, pts_right))

    # Draw the lane onto the warped blank image
    cv2.fillPoly(color_warp, np.int_([pts]), (0,255, 0))

    M, Minv = undist_warp.get_perspective_transform_matrices()

    # Warp the blank back to original image space using inverse perspective matrix (Minv)
    newwarp = cv2.warpPerspective(color_warp, Minv, (color_warp.shape[1], color_warp.shape[0])) 
    # Combine the result with the original image
    result = cv2.addWeighted(undistorted_color, 1, newwarp, 0.3, 0)
    cv2.putText(result, "Car offset: " + str(LEFT_LINE.mean_car_offset), (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),2)
    cv2.putText(result, "Left curvature: " + str(LEFT_LINE.mean_curvature), (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),2)
    cv2.putText(result, "Right curvature: " + str(RIGHT_LINE.mean_curvature), (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),2)
    if(verbose):
        plt.imshow(result)
        plt.show()

    return out_img, result


def test():

    mtx, dist = calibrate.get_mtx_dist()

    test_images_sl = glob.glob('./test_images/straight_lines*.jpg')
    test_images = glob.glob('./test_images/test*.jpg')

    i = 0
    for test_fname in test_images_sl + test_images:
        i+=1
        img = cv2.imread(test_fname)
        wrp, udst = undist_warp.warp(img, mtx, dist)
        lines, result = fit(wrp, udst, True, test_mode = True)
        plt.imsave('./output_images/lines' + str(i) + '.png', lines)
        cv2.imwrite('./output_images/result' + str(i) + '.jpg', result)

def image_process(image):
    mtx, dist = calibrate.get_mtx_dist()
    wrp, udst = undist_warp.warp(image, mtx, dist)
    out_img, result = fit(wrp, udst, verbose = False)
    return result


def fit_video():
    output = 'output.mp4'
    clip_input = VideoFileClip('project_video.mp4') #.subclip(41.6,43)
    clip_output = clip_input.fl_image(image_process)
    clip_output.write_videofile(output, audio=False)

fit_video()
#test()