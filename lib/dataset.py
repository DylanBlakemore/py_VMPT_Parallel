import numpy as np
import math

from lib import frame

class DataSet:
    def __init__(self, file_path, frame_size, num_frames=-1):
        self._file_data = np.genfromtxt(file_path, delimiter='\t') # load data from file
        # the number of lines to be used in the 
        self._frame_size = frame_size                              
        self._data_size = self._file_data.shape[0]                  # number of rows in the data
        if num_frames > 0 and num_frames < self._data_size:
            self._num_frames = num_frames
            self._file_data = self._file_data[0:num_frames*frame_size,:]
            self._data_size = np.shape(self._file_data)
        else:
            self._num_frames = int(math.ceil(self._data_size / float(self._frame_size)))  # number of frames, based on data set and frame size

    # Returns the total number of frames in the file
    def getNumFrames(self):
        return self._num_frames        
    
    # Returns the fframe of data at some index frame_num
    def getFrameAt(self, frame_num):
        if frame_num >= self._num_frames:
            return None
        else:
            frame_start = frame_num * self._frame_size
            frame_end = frame_start + self._frame_size
            
            # If the number f entries in the data is not exactly divisible by the frame size,
            # the beginning of the last frame is shifted back, such that the end of that frame
            # aligns with the end of the file
            if frame_end > self._data_size:
                frame_end = self._data_size
                frame_start = frame_end - self._frame_size
                
            frame_data = self._file_data[frame_start:frame_end, : ]
            return frame.Frame(frame_data)
        
    # For parallel computing, splits the data set up into chunks for processing
    def split(self):
        split_indices = range(self._frame_size, self._num_frames*self._frame_size, self._frame_size)
        return np.split(self._file_data, split_indices)
        
