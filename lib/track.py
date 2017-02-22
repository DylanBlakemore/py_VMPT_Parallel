# Class define a 'track', which contains a location history for a single tracer.
# All tracks for a given location set will have the same length, being equal to
# the number of unique time steps. Where a location does not exist at a time t_i,
# the location x_i is set to [nan, nan, nan] 
import numpy as np

class Track:
    def __init__(self, track_length, start_index, times, initial_point=None):
        self.MAX_SKIPS = 5          # The maximum number of consecutive skips before a track is terminated
        self.MIN_ENTRIES = 100      # The minimum number of entries needed for the track to be saved
        self.MIN_DENSITY = 0.5      # The minimum track density needed for the track to be saved
        self.EXTRAP_LEN = 15        # Number of entries used for extrapolation. Must be more than MAX_SKIPS
        self.QUAD_SIZE = 10          # Number of entries needed to use a quadratic extrapolation (less than EXTRAP_LEN)      
        
        self.START_INDEX = start_index # Location at which the actual entries start
        
        self.search_radius = 20
        
        self.n_skips = 0            # Number of consecutive skips
        self.length = track_length  # Total length of the track. Equal for all tracks.
        if initial_point is None:   # Empty initialization
            self.x_0 = np.array([np.nan, np.nan, np.nan])
            self.num_entries = 0
        else:
            self.x_0 = initial_point[0:3]
            self.num_entries = 1
            
        self.location_history = np.empty((self.length,3),float) 
        self.location_history.fill(np.nan)   # History is initialized to a matrix of NaN's  
        self.velocity_history = np.empty((self.length,3),float)
        self.velocity_history.fill(np.nan)   # Corresponding velocity history for track
        
        self.time_history = times
        
        self.pointer = start_index  # Index to the most recent entry
        
        self.location_history[self.pointer,:] = self.x_0
      
    # Adds an entry to the end of the track history.
    # new_location is a numpy array with format [x,y,z,t]
    def appendLocation(self, new_location):
        self.pointer = self.pointer + 1
        self.num_entries = self.num_entries + 1
        self.n_skips = 0
        
        self.location_history[self.pointer,:] = new_location
        
        self._updateVelocity()
        return None
    
    # Used when no new location is found for the new time step.
    def appendNone(self, new_time):
        self.pointer = self.pointer + 1
        self.n_skips = self.n_skips + 1
        self.num_entries = self.num_entries + 1
        return None
      
    # Returns the theoretical next position based on the most recent locations.
    # t_ext is the time for which the extrapolated position is calculated.
    def getExtrapolatedPosition(self, t_ext):
        end_extrap = self.pointer + 1
        if self.num_entries <= self.EXTRAP_LEN:
            start_extrap = self.START_INDEX
        else:
            start_extrap = end_extrap - self.EXTRAP_LEN
            
        # The most recent EXTRAP_LEN entries are used as data points for the extrapolation
        # (except in the case when there are fewer than EXTRAP_LEN entries total).
        # Once these entries are extracted, the ones that are actually used are those that 
        # do not have NaN values.
        extrap_set = self.location_history[start_extrap:end_extrap,:]
        extrap_times = self.time_history[start_extrap:end_extrap]
        
        extrap_indices = ~np.isnan(extrap_set).any(axis=1)
        
        extrap_set = extrap_set[extrap_indices]
        extrap_times = extrap_times[extrap_indices]
        
        # If the number of entries used in extrapolation is found to be less than EXTRAP_LEN,
        # a linear extrapolation method is used. If it is equal to or greater than QUAD_SIZE, 
        # a quadratic method is used.
        num_extrap_entries = extrap_set.shape[0]
        if num_extrap_entries < self.QUAD_SIZE:
            extrap_degree = 1
        else:
            extrap_degree = 2
        
        extrapolated = np.zeros(1,3)
        # For each of x,y & z vs t, fit a polynomial P_i to the data set and find P_i(t_ext)
        for i in range(0,3):
            xi_fit = np.polyfit(extrap_times, extrap_set[:,i], extrap_degree)
            xi_poly = np.poly1d(xi_fit)
            extrapolated[i] = xi_poly(t_ext)
        
        return extrapolated
    
    def getSearchRadius(self):
        #! Search radius should be defined in getExtrapolatedPosition, and should be a function
        #! of number of entries used for fitting and the RMSE of the fit. 
        return self.search_radius
    
    # Private method to update the history (positions, velocities etc.)
    def _updateVelocity(self):
        
        return None
        
    
            
        

