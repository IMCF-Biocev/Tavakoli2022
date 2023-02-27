import os
import logging
import numpy as np
import glob

from src.utils import read_axon, shift_axon


logging.basicConfig(level=logging.INFO)


def parse_raw_data(folder_name, group, name):
    """
    Parses raw data into the data suitable for measurements.

    :param folder_name: str, path to the folder with raw data
    :param group: str, name of the group
    :param name: str, name of the subfolder
    """
    logging.info(f"Parsing data from {folder_name}")

    try:
        # read raw data
        axons = read_axon(folder_name)
        logging.info(f"Number of time points is in file: {len(axons)}")

        # shift the axons to the single origin
        shifted_axons = shift_axon(axons)
        logging.info("Axons from different time points were shifted to the same origin")

        # extract growth data
        growth = np.array([axon[-1] for axon in shifted_axons])

        # save growth to CSV file
        output_dir = os.path.join("data", "parsed", group)
        os.makedirs(output_dir, exist_ok=True)

        output_path = os.path.join(output_dir, f"{name}.csv")
        np.savetxt(output_path, growth, delimiter=",", fmt="%10.5f")
        logging.info(f"Growth was saved to CSV file: {output_path}")

    except Exception as e:
        logging.error(f"Failed to parse data from {folder_name}: {str(e)}")


def main():
    """
    Main function to parse raw data in the 'data/raw' directory.
    """
    # check if 'data' folder exists
    if not os.path.exists('data'):
        raise Exception("No folder named 'data'")

    # check if 'data/raw' folder exists
    raw_data_dir = os.path.join('data', 'raw')
    if not os.path.exists(raw_data_dir):
        raise Exception("No folder named 'raw' in 'data'")

    # check if 'data/parsed' folder exists and create if not
    parsed_data_dir = os.path.join('data', 'parsed')
    os.makedirs(parsed_data_dir, exist_ok=True)

    # find all subfolders in 'data/raw' and parse them if they are not empty
    for group_folder in glob.glob(os.path.join(raw_data_dir, '*')):
        if not os.path.isdir(group_folder):
            continue

        group = os.path.basename(group_folder)
        logging.info(f"Parsing data from group: {group}")

        for subfolder in glob.glob(os.path.join(group_folder, '*')):
            if not os.path.isdir(subfolder):
                continue

            name = os.path.basename(subfolder)
            logging.info(f"Parsing data from subfolder: {name}")

            if os.listdir(subfolder):
                parse_raw_data(subfolder, group, name)
                logging.info(f"Data from {name} were parsed and saved to CSV file")
            else:
                logging.warning(f"Subfolder {name} is empty")


if __name__ == "__main__":
    main()
