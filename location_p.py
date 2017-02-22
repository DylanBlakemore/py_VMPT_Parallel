# built-in libraries
import numpy as np
import os
import glob
import shutil
import multiprocessing
from ConfigParser import SafeConfigParser

from sklearn.cluster import DBSCAN
# custom classes
from lib import dataset
from lib import frame
from lib import plotter
from lib import lofpy
from lib import vmptutils as vuti

## Constants used throughout the algorithm, imported from the config.ini file ##
config = SafeConfigParser()
config.read('lib/config.ini')

LINES_PER_TRACER = config.getint('Frame','Lines_Per_Tracer') # number of LOR's used per tracer
EPS = config.getfloat('Cluster','Eps')                       # search distance used in both LOF and DBSCAN. Also separation distance
K   = config.getint('Cluster','K')                           # number of points used in LOF and DBSCAN
MAX_OUTPUT = config.getint('LocationOutput','Max_Output')    # maximum number of entries in the output array before writing to disk
PERCENT_INC = config.getfloat('LocationOutput','Percent_Inc')# progress display increment
LOF_FRAC = config.getfloat('Filter','Lof_Frac')
VOL_FRAC = config.getfloat('Filter','Vol_Frac')
NUM_CORES = config.getint('Processing','Num_Cores')
########################

# if the number of cores to use is greater than the number
# of physical cores (or -1) set to maximum
if NUM_CORES > multiprocessing.cpu_count or NUM_CORES == -1:
    NUM_CORES = multiprocessing.cpu_count

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
              
num_tracers = int(raw_input('Enter the number of tracers expected: '))

# search the input folder for all files with the correct filetype (.dat)
print('Searching for .dat files in ' + input_folder)
search_path = os.path.join(input_folder,'*.dat')
input_files = glob.glob(search_path)

# define which files to triangulate
num_files = len(input_files)
start_file = 0
end_file = num_files
if end_file > num_files:
    end_file = num_files
    
# calculate the size (number of lines) of each frame
frame_size = LINES_PER_TRACER * num_tracers

