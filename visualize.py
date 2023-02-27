import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from src.utils import normalize_rotation
import os
from pathlib import Path

def folder_not_empty(folder):
    '''Check if folder exists and is not empty'''
    # check if folder exists
    if not os.path.isdir(folder):
        print(f"Folder '{folder}' does not exist. Please run 'python3 measure.py' to generate the data.")
        return False
    # check if folder is empty
    if not os.listdir(folder):
        print(f"Folder '{folder}' is empty. Please run 'python3 measure.py' to generate the data.")
        return False
    return True

def extract_data(df, genotype):
    '''Extract data from dataframe'''
    # get all unique values of 'NameOfMeasurement' column
    measurements = df['NameOfMeasurement'].dropna().unique()

    data = []
    data_times = []
    for measurement in measurements: # iterate over measurements
        # get df for current measurement
        df_measurement = df[df['NameOfMeasurement'] == measurement]
        # get Time column
        time = df_measurement['Time'].values
        path = df_measurement['CoordinateOfTip'].values
        new_path = np.array([np.fromstring(x[1:-1], sep=' ') for x in path])
        # if column Genotype is present, save the data
        if df_measurement['Genotype'].values[0] == genotype:
            data.append(new_path)
            data_times.append(np.array(time))
    return data, data_times

def plot_paths(ax, paths, paths_times, max_time, genotype):
    '''Plot paths and color them according to time'''
    # plot all arrays in a loop
    for i in range(len(paths)):
        # plot times as dots color them according to time
        ax.scatter(paths[i][:,0] + i * 10, paths[i][:,1], c=paths_times[i], cmap='viridis')
        # plot also each part of path with different color
        for j, (start, stop) in enumerate(zip(paths[i][:-1], paths[i][1:])):
            x, y = zip(start, stop)
            # comvert tuple to list
            x = list(x)
            y = list(y)
            # add value of i to x to make sure all plots are visible
            x = [i * 10 + j for j in x]
            color = plt.cm.viridis((paths_times[i][j] + paths_times[i][j+1])/ (2*max_time))
            ax.plot(x, y, color=color)
        
        # remove x axis ticks
        ax.set_xticks([])
        # set y limits to 125
        ax.set_ylim(0, 250)
        # set subplots label
        ax.set_title(genotype)

def find_max_time(data_times):
    max_time = 0
    for key in data_times:
        for value in data_times[key]:
            for i in value:
                if i > max_time:
                    max_time = i
    return max_time


def main():
    # check if folder exists and is not empty
    if not folder_not_empty("res"):
        exit()
    
    # read csv file
    data_folder = Path("res")
    df = pd.read_csv(data_folder / "measurements.csv")

    # get all unique values of 'Genotype' column
    genotypes = df['Genotype'].unique()

    # save to dict
    data = {}
    data_times = {}
    for genotype in genotypes:
        path, path_times = extract_data(df, genotype)
        data[genotype] = path
        data_times[genotype] = path_times

    # create a figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(20,10))

    max_time = find_max_time(data_times)

    # get all unique Time(sec) values from df
    times = df['Time'].unique()
    # remove nans from times
    times = times[~pd.isnull(times)]
    # interpolate times to get 100 values
    times = np.interp(np.linspace(0, len(times), 1000), np.arange(len(times)), times)
    # create a colorbar
    cbar = fig.colorbar(plt.cm.ScalarMappable(cmap='viridis'), ax=[ax1, ax2], values=times)
    # create a colorbar using the max time and 0 as limits and add max time as label
    cbar.set_label('Time', rotation=270, labelpad=15)

    for genotype, ax in zip(genotypes, [ax1, ax2]):
        rotated_paths = normalize_rotation(data[genotype])
        paths_times = data_times[genotype]
        # plot paths for each genotype
        plot_paths(ax, rotated_paths, paths_times, max_time, genotype)

    # save figure to file
    fig.savefig('res/paths.png')

if __name__ == "__main__":
    main()
