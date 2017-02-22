import numpy as np
from scipy.spatial import Voronoi
import vmptlib

import lor

class Frame:
    def __init__ (self, frame_data):
        self._frame_data = frame_data
        self._num_rows = self._frame_data.shape[0]
        self._lines = []
        self._frame_time = 0.0
        self._spacing = 1.0
        
        self._generateLines()
    
    # returns the time of the frame - the average of all the line times
    def getFrameTime(self):
        return self._frame_time
        
    # returns the points with the smallest Voronoi regions per line
    def getPointsOfInterest(self, spacing):
        self._spacing = spacing
        self._generateSeedPoints()

        voro = Voronoi(self._all_points)    
                 
        points, volumes = vmptlib.getSmallestRegion(int(len(self._lines)),
                                           self._line_indices.tolist(),
                                           voro.point_region.tolist(),
                                           voro.regions,
                                           voro.vertices)
      
        return {'ind':points, 'vol':volumes}
    
    # returns the locations of the points at the specified indices
    def getPointsAt(self, indices):
        return self._all_points[indices,:]
    #------------------------------------------------------------------------#     
        
    # creates a list of LineOfResponse objects from the raw frame data
    def _generateLines(self):
        t_total = 0.0
        
        for row in range(0, self._num_rows):
            A = self._frame_data[row,0:3]
            B = self._frame_data[row,3:6]
            t_total += self._frame_data[row,6]
            
            self._lines.append(lor.LineOfResponse(A, B, row))
        
        self._frame_time = t_total/self._num_rows    
        
    # discretizes the LOR's and creates containers to track which points belong
    # to which lines
    def _generateSeedPoints(self):
        total_points = 0
        for line in self._lines: # count the total number of points that will be used in the tessellation
            total_points += line.getNumPoints(self._spacing)
            
        total_points = int(total_points)
        # create an array of zeros to be populated with Voronoi seeds
        self._all_points = np.zeros((total_points,3))
        self._line_indices = np.zeros((total_points))
        
        current_row = 0
        for line in self._lines:
            num_points = line.getNumPoints(self._spacing)
            self._all_points[current_row:current_row + num_points,:] = line.getLineDiscretization(self._spacing)
            self._line_indices[current_row:current_row + num_points] = line.getLineID()
            self._line_indices = self._line_indices.astype(int)
            
            current_row += num_points            
        
        
        
