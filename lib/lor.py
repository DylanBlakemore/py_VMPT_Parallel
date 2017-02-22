import numpy as np
import math

class LineOfResponse:

    def __init__(self, A, B, lineID):
        self._A = A # row vector
        self._A.shape = (1,3)
        self._B = B # row vector
        self._B.shape = (1,3)
        self._V = B - A #vector from B to A
        self._line_ID = lineID
        self._length = np.linalg.norm(self._A - self._B)
        
    def getNumPoints(self, spacing):
        num_points = math.floor(self._length/spacing) + 1# numper of discrete points
        return int(num_points)
        
    def getLineID(self):
        return self._line_ID
        
        
    # let point x_i be some point along a line defined by B - A
    # then x_i = A + ri(B - A)
    # where i = 1 ... num_points and
    # r = 1/num_points
    def getLineDiscretization(self, spacing):
        num_points = self.getNumPoints(spacing)
        r = 1.0/(num_points - 1.0)
        
        i_array = np.arange(num_points)
        i_array.shape = (num_points, 1)
        A_mat = np.tile(self._A, (num_points, 1))
        
        x = A_mat + r * (np.matmul( i_array, self._V ))
        
        return x
        
        
        
    
        