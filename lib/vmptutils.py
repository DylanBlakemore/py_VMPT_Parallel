import numpy as np
import os.path
    
def getLowFraction(data, fraction):
    sorted_data = list(data)
    sorted_data.sort()
    largest_valid = sorted_data[int(len(data) * fraction)]
    
    indices = np.argwhere(data <= largest_valid)
        
    return indices[:,0]
    
def writeOutputToFile(output_folder, location_output):
    stripped_location = location_output[~np.all(location_output == 0, axis=1)] # removes trailing rows of zeros
    output_fname = output_folder + "/locations.csv"
    
    if os.path.isfile(output_fname):
        f_handle = open(output_fname, 'a')
        np.savetxt(f_handle, stripped_location, delimiter=',')
        f_handle.close()
    else:
        np.savetxt(output_fname, stripped_location, delimiter=',')
    return None
    
def printProgress(file_num, progress, average_tracers):
    print('-')
    print("File " + str(file_num + 1) + " progress: " + str(progress) + "%")
    print("Average number of tracers per frame: %.2f" % average_tracers)
    
    

