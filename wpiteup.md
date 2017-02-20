
[//]: # (Image References)

[image1]: ./examples/undistort_output.png "Undistorted"
[image2]: ./test_images/test1.jpg "Original"
[image3]: ./test_images/test1.jpg "Undistorted"
[image4]: ./output_images/undistorted5.jpg "Undistorted"
[image5]: ./output_images/color_transformed5.jpg "Binary Transformed"
[image6]: ./output_images/undistorted4.jpg "Undistorted"
[image7]: ./output_images/warped4.jpg "Warped"
[image8]: ./examples/binary_combo_example.jpg "Binary Example"
[image9]: ./examples/warped_straight_lines.jpg "Warp Example"
[image10]: ./examples/color_fit_lines.jpg "Fit Visual"
[image12]: ./examples/example_output.jpg "Output"
[video1]: ./project_video.mp4 "Video"

##Advanced Line Finding

#Camera Calibration

To calibrate the camera checkers board images in camera_cal repository subfolder were used. All images are taken of a checkers board with (9, 6) corners. OpenCV findChessboardCorners method is used on a greyscaled images to find exact corners locations.Those locations are used as an input to calibrateCamera function to find camera matrix and distortion coefficients. All the calibration code is loceted in [calibration.py](calibration.py) file.

![alt text][image1]

#Pipeline

The camera matrix was then used to undistort test images in CarND-Advanced-Lane-Lines\test_images.

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

Then using getPerspectiveTransform method for constructing perspective matrix (and inverse for later) and warpPerspective for actual transform of binary image, we got lines seen from above like this (see [undist_warp.py](undist_warp.py)):

![alt text][image6]
![alt text][image7]

The code in [sliding_windows.py](sliding_windows.py) is used to identify pixels of the line and then fit polynomial to it. There are two paths of how it may be done depending on the sequence of images being fed to fit method: detectiong lines using 9 sliding windows and detecting lines  

Line class in [line.py](line.py) is used to store valuable information of the left and right lines across the stream of input images, such as last 4 sets of fitted polynomial coefficients, current fit, average fit, current curvature. This data is used to make a decision whether polynomial coefficients detected in current video frame correspond in a sensible way to coefficients fitted in the previous frames as well as whether left and right lines are sensibly positioned on the frame. Assumprions that are made to produce the project video are thefollowing: 

1) We always trust the first frame because we have no data yet.
2) If left line was not considered detected, we discard the right line from this frame automatically. 





 

