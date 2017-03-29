
[//]: # (Image References)

[image1]: ./output_images/calibration1.jpg "Distorted Chessboard"
[image1.5]: ./output_images/undistorted_chessboard.jpg "Undistorted Chessboard"
[image2]: ./test_images/test1.jpg "Original"
[image3]: ./output_images/undistorted3.jpg "Undistorted"
[image4]: ./output_images/undistorted5.jpg "Undistorted"
[image5]: ./output_images/color_transformed5.png "Binary Transformed"
[image6]: ./output_images/undistorted4.jpg "Undistorted"
[image7]: ./output_images/warped4.png "Warped"
[image8]: ./output_images/line4.png "Detected Lines"
[image9]: ./output_images/undistorted4.jpg "Undistorted"
[image10]: ./output_images/result4.jpg "Output"
[video1]: ./output.mp4 "Video"

# Advanced Line Finding

## Camera Calibration

To calibrate the camera checkers board images in *camera_cal* repository subfolder were used. All images are taken of a checkers board with (9, 6) corners. OpenCV *findChessboardCorners* method is used on a greyscaled images to find exact corners locations.Those locations are used as an input to *calibrateCamera* function to find camera matrix and distortion coefficients. All the calibration code is located in [calibrate.py](calibrate.py) file.

![alt text][image1]
![alt text][image1.5]

## Pipeline (Test Images)

The camera matrix was then used to undistort test images in *CarND-Advanced-Lane-Lines\test_images*.

Example of test image before and after distortion. 
 
![alt text][image2]
![alt text][image3]

Then after playing with HSV and HLS color transformations, Sobel operator, magnitude and direction of gradient thresholds (all code located in [color_transform.py](color_transform.py)), I ended up using the following combination of thresholds (see combine method for the code): binary OR between two groups 1) intersection between absolute sobel x and y between 20 and 100 and magnitude threshold between 30 and 100 and 2) S channel of HLS transformed image between 90 and 255 and gradient directory threshold between 0.7 and 1.3.
 
![alt text][image4]
![alt text][image5]

After this, I defined a trapezoid on first two (straight lined) test images and taking average of two I have got the following source and destination shapes for perspective transform:


| Source        | Destination   | 
|:-------------:|:-------------:| 
| 595, 450      | 219, 0        | 
| 259, 687      | 219, 720      |
| 1056, 687     | 1091, 720     |
| 687, 450      | 1091, 0       |

Then using *getPerspectiveTransform* method for constructing perspective matrix (and inverse for later) and *warpPerspective* for actual transform of binary image, we got lines seen from above like this (see [undist_warp.py](undist_warp.py)):

![alt text][image6]
![alt text][image7]

The code in [sliding_windows.py](sliding_windows.py) is used to identify pixels of the line and then fit polynomial to it. There are two paths of how it may be done depending on the sequence of images being fed to fit method: detecting lines using 9 sliding windows and detecting lines using areas around lines detected in the previous frame. 

Line class in [line.py](line.py) is used to store valuable information of the left and right lines across the stream of input images, such as last 4 sets of fitted polynomial coefficients, current fit, average fit, current curvature. This data is used to make a decision whether polynomial coefficients detected in current video frame correspond in a sensible way to coefficients fitted in the previous frames as well as whether left and right lines are sensibly positioned on the frame. Assumptions that are made to produce the project video are the following: 

* We always trust the first frame with lines detected using sliding windows.
* If left line was not considered detected, we discard the right line from this frame automatically.
* We care about next curvature being close to previous curvature and curvature of the other line in this frame when both are relatively small.
* Next fitted polynomial coefficients have to be close to the previous ones and to the ones of the other line in this frame

When the above conditions are met the new pair of lines is considered "detected", fitted polynomial coeffitients are added to the queue of four latest fits and the average of what is in the queue is considered as fit for the current frame. If lines are detected in the current frame, the next frame will not use sliding windows but just area arounf currently detected lines. When lines are lost, the sliding windows come in play again.

![alt text][image7]
![alt text][image8]

The curvature radius in meters is also calculated in [sliding_windows.py](sliding_windows.py), see lines 1123-127. We take already detected left and right line pixels, multiply them using pixel to meter conversions and fit polynomials to the result points. This way we obtain real valued polynomial coefficients to feed into curvature radius formula.

The car offset from the center of the image is calculated in [sliding_windows.py](sliding_windows.py), see lines 134-136.

Both curvature and car offset are then passed to *set_output_params* method of [line.py](line.py) where they are evaluated, added to the lists of recent mesurements if they are of a good quality and averaged against 4 most recent records. We change values once in 4 frames to make it readable for the user.

Then warped image with the detected lines is transformed back using inverse perspective transform matrix and overlayed on the color undistorted image.

![alt text][image9]
![alt text][image10]

## Pipeline (Video)

Project video is fed into the pipeline described in the previous section. See the result video with detected lane below:

[output.mp4](output.mp4)

## Discussion

The created pipeline gives a good result on the project video. However, all the color and gradient binary thresholding was manually fine-tuned using test frames from the input video. This may become a problem in a different scenery or nighttime video. It would be interesting to train threshold coeffitients of possible image transformations on a set of different videos to minimise quantity of white pixels outside actual lines areas. Likewise, thresholds in the Line class in [line.py](line.py) were also tuned against the test video and are better learned as a combination of some video frames parameters. Finally, taking the average of n latest detections is constant along the way but has to be dependent on the car speed. 


   
  





 

