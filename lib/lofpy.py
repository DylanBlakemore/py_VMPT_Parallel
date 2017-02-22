from sklearn.neighbors import NearestNeighbors
import numpy as np

def getLOF(k, X):
    num_points = X.shape[0]
    lof = np.zeros((num_points,1), np.float)
    lrd = np.zeros((num_points,1), np.float)
    # determine the k nearest neighbours in the set X
    nbrs = NearestNeighbors(n_neighbors=k+1).fit(X)
    distances, indices = nbrs.kneighbors(X)
    
    # find the k-distance for each point
    kdistances = distances[:,-1]
    
    for i in range(0, num_points):
        # calculate the reachability distance for the  i-th point
        i_nbrs = indices[i,1:]
        i_kdist = kdistances[i_nbrs]
        i_reach_dist = np.maximum(distances[i,1:],i_kdist)
        # calculate the lrd for the i-th point
        lrd[i] = float(k) / np.sum(i_reach_dist)
        
    for j in range(0, num_points):
        j_nbrs = indices[j,1:]
        lof[j] = (np.sum(lrd[j_nbrs]) / float(k)) / lrd[j]
           
    return lof