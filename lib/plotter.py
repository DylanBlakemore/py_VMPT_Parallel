from mpl_toolkits.mplot3d import Axes3D
import scipy.stats
import matplotlib.pyplot as plt
import numpy as np

def scatter3D(data):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    
    x = data[:,0]
    y = data[:,1]
    z = data[:,2]
    
    ax.scatter(x,y,z, c='r', marker='o')
    
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    
    plt.show()
    
def scatterClusters(points, labels):
    return None
    
def histogram(data, nbins=None,
                      title=None,
                      xlabel=None,
                      ylabel=None):
    
    if title is None:
        title = 'Histogram'
    if xlabel is None:
        xlabel = 'Value'
    if ylabel is None:
        ylabel = 'Frequency'
        
    if nbins is None:
        plt.hist(data)
    else:
        plt.hist(data, bins=nbins)
    
    plt.show()
    
def cumulativeFrequency(data, nbins=None):
    data.sort()
    fig, ax = plt.subplots(1,1)
    if nbins is None:
        density, base = np.histogram(data)
        ax.hist(data, cumulative=True)
    else:
        density, base = np.histogram(data, bins=nbins)
        ax.hist(data, bins=nbins, cumulative=True)
    
    dist_name = 'expon'
    dist = getattr(scipy.stats, dist_name)
    param = dist.fit(data)
    cdf_fitted = dist.cdf(data, *param[:-2], loc=param[0],scale=param[1]) * len(data)
    ax.plot(data, cdf_fitted, c='r')
    plt.show()
