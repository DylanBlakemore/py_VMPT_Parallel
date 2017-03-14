# built-in libraries
import numpy as np
import os
import glob
import shutil
import multiprocessing
import time
from ConfigParser import SafeConfigParser
from sklearn.cluster import DBSCAN
# custom classes
from lib import dataset
from lib import frame
from lib import lofpy
from lib import vmptutils as vuti


#==============================================================================
#     This is the method that is called by the Pool object, and
#     which runs in parallel across the desired number of CPU cores.
#     It takes one frame of data as a parameter and determines the locations 
#     of the tracers within that frame
#==============================================================================
def locate(frame_data_i):
    # Create a Frame object from the data
    frame_i = frame.Frame(frame_data_i)
    # Discretize LOR's and generate Voronoi tessellations to determine the 
    #   smallest cell for each LOR.
    poi = frame_i.getPointsOfInterest(EPS)
    all_points = frame_i.getPointsAt(poi['ind'])
    all_vols = poi['vol']
    # Get the average time for the frame
    time_i = frame_i.getFrameTime()
    del frame_i
    # Perform a Local Outlier Factor analysis on the points of interest
    lof = lofpy.getLOF(K, all_points)
    low_lof = vuti.getLowFraction(lof, LOF_FRAC)
    lof_smoothed = all_points[low_lof,:]
    lof_smoothed_vols = np.array(all_vols)[low_lof]
    # Clean the data further by discarding the points with large Voronoi cells
    low_vol = vuti.getLowFraction(lof_smoothed_vols, VOL_FRAC)
    remainders = lof_smoothed[low_vol,:]
    # Perform DBSCAN clustering
    db = DBSCAN(eps=EPS, min_samples=K).fit(remainders)
    labels = db.labels_
    n_clusters = len(set(labels)) - (1 if -1 in labels else 0)
    locations = np.zeros((n_clusters,4))
    # Calculate geometric mean of each cluster
    for cluster in range(0, n_clusters):
        cluster_inds = np.where(labels == cluster)[0]
        location = np.sum(remainders[cluster_inds,:], axis=0)/len(cluster_inds)
        locations[cluster,0:3] = location
        locations[cluster,3] = time_i
    #end if
    return locations
#end locate() method

#==============================================================================
#     Called when a thread is created.
#==============================================================================
def start_process():
    print 'Starting ', multiprocessing.current_process().name
#end start_process() method

#==============================================================================
#     Main method.
#     Initiates constants used in the process by loading the config.ini file.
#     Asks for user input, namely for the folder containing the input files,
#         the folder to which the output will be written, and the number
#         of tracers used in the experiment.
#     For each input file, the data is split into frames. The set of frames is
#         passed to the Pool object to be used as parameters for the locate 
#         method.
#     After a file has been processed, the output is written to the output file.
#==============================================================================
if __name__ == "__main__":
    ## Constants used throughout the algorithm, imported from the config.ini file ##
    config = SafeConfigParser()
    config.read('lib/config.ini')
    
    global EPS, K, LOF_FRAC, VOL_FRAC
    LINES_PER_TRACER = config.getint('Frame','Lines_Per_Tracer') # number of LOR's used per tracer
    EPS = config.getfloat('Cluster','Eps')                       # search distance used in both LOF and DBSCAN. Also separation distance
    K   = config.getint('Cluster','K')                           # number of points used in LOF and DBSCAN
    MAX_OUTPUT = config.getint('LocationOutput','Max_Output')    # maximum number of entries in the output array before writing to disk
    PERCENT_INC = config.getfloat('LocationOutput','Percent_Inc')# progress display increment
    LOF_FRAC = config.getfloat('Filter','Lof_Frac')
    VOL_FRAC = config.getfloat('Filter','Vol_Frac')
    NUM_CORES = config.getint('Processing','Num_Cores')
    
    # if the number of cores to use is greater than the number
    # of physical cores (or -1) set to maximum
    if NUM_CORES > multiprocessing.cpu_count:
        print('Number of cores requested greater than physical count. Using maximum.')
        NUM_CORES = multiprocessing.cpu_count
    #end if
    if NUM_CORES == -1:
        print('Using maximum number of cores.')
        NUM_CORES = multiprocessing.cpu_count
    #end if
    
    # get user input
    input_folder = raw_input('Enter the path of the folder containing the input files: ')
    # create the ouput folder (delete first if it exists)
    folder_exists = 1
    while folder_exists:
        output_folder = raw_input('Enter the name of the folder to which the output will be written: ')
        folder_exists = os.path.exists(output_folder)
        if folder_exists:
            delete_folder = raw_input("Folder exists, delete? (y/n) ")
            if delete_folder == "y" or delete_folder == "Y":
                shutil.rmtree(output_folder)
                os.makedirs(output_folder)
                folder_exists = 0
        else:
            os.makedirs(output_folder)
        #end if
    #end while folder_exists
                  
    num_tracers = int(raw_input('Enter the number of tracers expected: '))
    
    print('Starting location using ' + str(NUM_CORES) + ' physical cores.')
    
    # search the input folder for all files with the correct filetype (.dat)
    print('\n Searching for .dat files in ' + input_folder)
    search_path = os.path.join(input_folder,'*.dat')
    input_files = glob.glob(search_path)
    
    # define which files to triangulate
    num_files = len(input_files)
    start_file = 0
    end_file = num_files
    if end_file > num_files:
        end_file = num_files
    #end if
        
    # calculate the size (number of lines) of each frame
    frame_size = LINES_PER_TRACER * num_tracers
    
    for file_num in range(start_file, end_file):
        try:
            file_path = input_files[file_num]
            print('==================================================')
            print('Loading data from file ' + file_path)
            data_file = dataset.DataSet(file_path, frame_size);
            pool_inputs = data_file.split()
            print('Data loaded')
            pool = multiprocessing.Pool(processes=NUM_CORES, initializer=start_process)
            
            start = time.time()
            pool_output = pool.map(locate, pool_inputs)
            pool.close()
            pool.join()
            end = time.time()
            
            print('Finished processing ' + str(data_file.getNumFrames()) + ' frames of file: ' \
                   + file_path + ' in ' + str(end-start) + 's')
            vuti.writeOutputToFile(output_folder, np.vstack(np.array(pool_output)))
        except KeyboardInterrupt, SystemExit:
            pool.close()
            pool.join()
            print('\n Operation cancelled, writing data to file...')
            vuti.writeOutputToFile(output_folder, np.vstack(np.array(pool_output)))
            raise
        #end try
    #end for file_num
#end main