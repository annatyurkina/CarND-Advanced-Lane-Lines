import numpy as np

class Line():
    def __init__(self):
        # was the line detected in the last iteration?
        self.detected = False  
        # x values of the last n fits of the line
        self.recent_xfitted = [] 
        #average x values of the fitted line over the last n iterations
        self.bestx = None   
        # fit coeffitients of the last n fits of the line
        self.recent_fit = []   
        #polynomial coefficients averaged over the last n iterations
        self.best_fit = None  
        #polynomial coefficients for the most recent fit
        self.current_fit = np.array([0,0,0], dtype='float')   
        #radius of curvature of the line in some units
        self.radius_of_curvature = None 
        #distance in meters of vehicle center from the line
        self.line_base_pos = None 
        #difference in fit coefficients between last and new fits
        self.diffs = np.array([0,0,0], dtype='float') 
        #x values for detected line pixels
        self.allx = None  
        #y values for detected line pixels
        self.ally = None
        #last fit bad quality
        self.last_fit_suspitious = False
        #last fit bad quality
        self.recent_curvatures = []
        #last fit bad quality
        self.mean_curvature = None
        #last fit bad quality
        self.recent_car_offsets = []
        #last fit bad quality
        self.mean_car_offset = None
        #last fit bad quality
        self.output_frames = 0

    def was_detected(self, next_x, next_curvature, next_fit, next_other_curvature, next_other_fit, other_line_not_detected = False, verbose = True, test_mode = False):
        if(test_mode):
            self.best_fit = next_fit
            return
        prev_detected = self.detected
        this_detected = self.best_fit == None or ((np.abs(self.radius_of_curvature - next_curvature) < 5000  or (self.radius_of_curvature > 5000 and next_curvature > 5000)) and \
            (np.abs(self.current_fit - next_fit) < [0.005, 2.0, 150.0]).all() and \
            (np.abs(next_other_curvature - next_curvature) < 5000  or (next_other_curvature > 5000 and next_curvature > 5000)) and \
            (np.abs(next_other_fit[0] - next_fit[0]) < 0.001) and \
            (np.abs(next_other_fit[1] - next_fit[1]) < 0.5))
        self.detected = not prev_detected or not other_line_not_detected and this_detected

        if(not self.bestx == None and verbose):
            print('curvature to last')
            print((np.abs(self.radius_of_curvature - next_curvature) < 5000  or (self.radius_of_curvature > 5000 and next_curvature > 5000)))
            print(self.radius_of_curvature)
            print(next_curvature)
            print('fit to last')
            print((np.abs(self.current_fit - next_fit) < [0.005, 2.0, 150.0]))
            print(self.current_fit)
            print(next_fit)
            print('curvature to other')
            print(np.abs(next_other_curvature - next_curvature) < 5000 or (next_other_curvature > 5000 and next_curvature > 5000)) 
            print(next_curvature)
            print(next_other_curvature)
            print('fit to other')
            print((np.abs(next_other_fit[0] - next_fit[0]) < 0.001))
            print((np.abs(next_other_fit[1] - next_fit[1]) < 0.5))
            print(next_fit[0])
            print(next_other_fit[0])
            print(next_fit[1])
            print(next_other_fit[1])

        if(self.detected):
            if(len(self.recent_xfitted) >= 4):
                self.recent_xfitted.pop(0)
            self.recent_xfitted.append(next_x)
            self.bestx = np.mean(self.recent_xfitted, axis=0)
            if(len(self.recent_fit) >= 4 and not self.last_fit_suspitious):
                self.recent_fit.pop(0)
            if(self.last_fit_suspitious):
                self.recent_fit.pop()
            self.last_fit_suspitious = not this_detected
            self.recent_fit.append(next_fit)
            self.best_fit = np.mean(self.recent_fit, axis=0)
            self.current_fit = next_fit
            self.radius_of_curvature = next_curvature


    def set_output_params(self, curvature, car_offset):
        if(self.detected):
            if(len(self.recent_curvatures) >= 4 and not self.last_fit_suspitious):
                self.recent_curvatures.pop(0)
                self.recent_car_offsets.pop(0)
            if(self.last_fit_suspitious):
                self.recent_car_offsets.pop()
                self.recent_curvatures.pop()
            self.recent_curvatures.append(curvature)
            self.recent_car_offsets.append(car_offset)
            if(self.output_frames == 0):
                self.mean_curvature = np.mean(self.recent_curvatures)
                self.mean_car_offset = np.mean(self.recent_car_offsets)
            if(self.output_frames >= 4):
                self.output_frames = 0
            else:
                self.output_frames+=1


