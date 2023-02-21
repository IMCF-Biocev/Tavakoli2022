import os
from natsort import natsorted
import numpy as np
import re
from collections import defaultdict
import pandas as pd
import matplotlib.pyplot as plt

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

def measure(shifted_axons, measurements, prev_tip, columns, origin, name):
    ''' Measure axons and save the results to measurements dictionary'''

    total_growth = np.linalg.norm(shifted_axons[-1][-1] - shifted_axons[0][-1])
    total_speed = total_growth / len(shifted_axons)

    # compute total angle change
    x = shifted_axons[0][-1]
    x = x / np.linalg.norm(x)

    y = shifted_axons[-1][-1]
    y = y / np.linalg.norm(y)

    angle = np.degrees(np.arccos(x @ y))

    for i, axon in enumerate(shifted_axons):
        measurements[columns[0]].append(name) # add name of a measurement
        current_time = i
        print('time:', current_time)
        measurements[columns[1]].append(current_time) # add time to measurements

        # add coords to measurements
        print('last tip is', axon[-1])
        measurements[columns[2]].append(axon[-1])

        # compute the distance between first and last coord and add it to measurements
        axon_length = np.linalg.norm(origin - axon[-1])
        print('axon growth at time', current_time, 'is', axon_length)
        measurements[columns[3]].append(axon_length)

        current_tip = axon[-1]
        
        if i == 0:
            growth_dist = 0
            speed = 0
            angle = 0
        else: 
            growth_dist = np.linalg.norm(current_tip - prev_tip)
            speed = growth_dist / (current_time - prev_time)
            
            prev_prev_tip = shifted_axons[i - 2][-1] if i >= 2 else origin

            x = prev_prev_tip - prev_tip
            x = x / np.linalg.norm(x)

            y = current_tip - prev_tip
            y = y / np.linalg.norm(y)

            angle = np.degrees(np.arccos(x @ y))

        # add speed to measurements
        print('speed of growth at time', current_time, 'is', speed)
        measurements[columns[4]].append(speed)
        measurements[columns[5]].append(growth_dist)
        
        
        print('angle change at time', current_time, 'is', angle)
        measurements[columns[6]].append(180 - angle)
        
        prev_tip = current_tip
        prev_time = current_time

        measurements[columns[7]].append(np.nan)
        measurements[columns[8]].append(np.nan)
        measurements[columns[9]].append(np.nan)

    first_axon = shifted_axons[0][-1]
    first_axon = first_axon / np.linalg.norm(first_axon)
    # compute the angle between the first and last axon
    total_angle = np.degrees(np.arccos(first_axon @ y))
    
    # use matplotlib to plot vectors 
    # plt.quiver([0, 0], [0, 0], [origin[0], y[0]], [origin[1], y[1]], angles='xy', scale_units='xy', scale=1)
    
    # plt.quiver([0, 0], [0, 0], [origin[0], first_axon[0]], [origin[1], first_axon[1]], angles='xy', scale_units='xy', scale=1)
    # plt.xlim(-1, 1)
    # plt.ylim(-1, 1)
    # plt.show()

    measurements[columns[7]][-1] = total_growth
    measurements[columns[8]][-1] = total_speed
    measurements[columns[9]][-1] = total_angle

    measurements = pd.DataFrame(measurements)
    measurements.to_csv('measurements.csv', index=False)

    return measurements


#     # print('what is the name of a measurement?')
# name = 'x'
# # print('where is it located?')
# folder_name = 'data'

# axons = read_axon(folder_name)

# shifted_axons = shift_axon(axons)

# # check if there is already a file with measurements
# if os.path.isfile(f'measurements.csv'):
#     measurements = pd.read_csv('measurements.csv')
#     # create dictionary from the dataframe
#     measurements = measurements.to_dict('list')
# else:
#     measurements = defaultdict(list) # set measurements dictionary

# # set columns names 
# columns = ['Name of a measurement', 'Time', 'Coordinate of the tip node', 'Axon length ($\mu m$)', 'Speed from $t_{i-1}$ to $t_{i}$ ($\mu m / \text{sec}$)',
#         'Axon growth distance from $t_{i-1}$ to $t_{i}$ ($\mu m$)',  'Angle change from $t_{i-1}$ to $t_{i}$ (%)', 'Total growth during all time ($\mu m$)', 
#         'Total speed during all time ($\mu m / \text{sec}$)', 'Total angle change (%)']

# origin = shifted_axons[0][0] # set origin
# prev_tip = origin

# measurements = measure(shifted_axons, measurements, prev_tip, columns, origin, name)