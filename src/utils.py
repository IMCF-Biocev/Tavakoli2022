import os
from natsort import natsorted
import numpy as np
import re
import pandas as pd

def read_axon(folder_name):
    '''Reads the axon tracing data from the folder and returns the data as an array'''
    files =  os.listdir(folder_name + '/') 
    files = natsorted(files)

    axons = [] # the array that would keep information about axons, their coordinates. 

    for file in enumerate(files):
        # load parse the data
        with open(folder_name + '/' + file[1], 'r') as f: # read swc as txt file
            data = f.read()

        # split into lines and take only lines that start with a number
        lines = [line for line in data.split('\n') if re.match(r"^\d+.*$",line)] 
        coords = [np.array(w.split('\t')[2].split(' ')[:2], dtype=float) for w in lines if re.match(r"^\d+.*$",w)]
        axon = np.array(coords)
        axons.append(axon)
    return axons

def shift_axon(axons):
    '''Shifts the axon to align origins in all time points'''
    # shift the axons to the single origin
    origin = axons[0][0]
    shifted_axons = [axons[0]]

    # subtract the origin from each axon
    for i, axon in enumerate(axons):
        if i == 0: continue
        diff = axon[0] - origin
        shifted_axon = np.array([coord - diff for coord in axon])
        shifted_axons.append(shifted_axon)

    # move origin to 0
    shifted_axons = [axons - origin for axons in shifted_axons]
    return shifted_axons

def measure(arr, measurements, columns, genotype, sample, name_of_measurement):
    ''' Measure axons and save the results to measurements dictionary'''
    origin = arr[0] # first coord

    total_growth = np.linalg.norm(arr[-1] - origin) # compute total growth distance as a norm of total vector of growth
    total_speed = total_growth / len(arr) # compute total speed as a total growth distance divided by the number of time points
    
    # compute total angle change
    x = origin / np.linalg.norm(origin) # normalize the vector

    y = arr[-1] # last coord
    y = y / np.linalg.norm(y) # normalize the vector

    total_angle = np.degrees(np.arccos(x @ y))

    prev_node = origin
    prev_time = 0

    for i, node in enumerate(arr):
        measurements[columns[0]].append(genotype) # add name of a measurement
        measurements[columns[1]].append(sample) # add sample
        measurements[columns[2]].append(name_of_measurement) # add name of a measurement
        current_time = i
        measurements[columns[3]].append(current_time) # add time to measurements

        # add coords to measurements
        measurements[columns[4]].append(node)

        # compute the distance between first and last coord and add it to measurements
        axon_length = np.linalg.norm(node - origin)
        measurements[columns[5]].append(axon_length)
        
        if i == 0:
            growth_dist = 0
            speed = 0
            angle = 0
        else: 
            growth_dist = np.linalg.norm(node - prev_node) # compute growth distance as a norm of a vector between two points
            speed = growth_dist / (current_time - prev_time) # compute speed as a distance between two points divided by the time difference, even though time difference is always 1 in our case
            
            prev_prev_node = arr[i - 2] if i >= 2 else origin

            x = prev_prev_node - prev_node
            x = x / np.linalg.norm(x)

            y = node - prev_node
            y = y / np.linalg.norm(y)

            angle = np.degrees(np.arccos(x @ y))

        # add speed to measurements
        measurements[columns[6]].append(speed)
        measurements[columns[7]].append(growth_dist)
        measurements[columns[8]].append(180 - angle)
        
        prev_node = node
        prev_time = current_time

        measurements[columns[9]].append(np.nan)
        measurements[columns[10]].append(np.nan)
        measurements[columns[11]].append(np.nan)
    

    measurements[columns[9]][-1] = total_growth
    measurements[columns[10]][-1] = total_speed
    measurements[columns[11]][-1] = total_angle

    measurements = pd.DataFrame(measurements)
    # measurements.to_csv('measurements.csv', index=False)

    return measurements


# make a function that would normalize rotation between axons
def normalize_rotation(array):
    # normalize each subarray to start at 0,0
    array = [a - a[0] for a in array]
    # for each subarray, find the angle between the first and last point
    rotated_array = []
    for i, a in enumerate(array):
        # if any element of a is negative, flip the vector
        # remove the negative sign in the y axis
        a[:,0] = np.abs(a[:,0])
        x = [0,1]
        y = [np.mean(a[:,0]), np.mean(a[:,1])]
        y = y / np.linalg.norm(y)
        theta = np.arccos(x @ y)
        # construct a rotation matrix to rotate the subarray by that angle
        c, s = np.cos(theta), np.sin(theta)
        R = np.array(((c, -s), (s, c)))
        # rotate the subarray
        a = R @ a.T
        rotated_array.append(a.T)
    return rotated_array
