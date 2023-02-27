# Tracing and measurements of axons during development
This project is aimed at analyzing axon growth data to measure various growth parameters and generate a csv report on the findings. The raw data are coming from Fiji's [SNT plugin](https://imagej.net/plugins/snt/) manual axon tracing. These data are parsed and processed to extract information about axons growth over time, which is then used to generate the measurements report.

## Installation
To use this project, you will need to have Python 3.9 or later installed on your system. You can download Python from the official website.

You will also need to install the following packages:

numpy
pandas
glob

You can install these packages using pip by running the following command:
```
pip install numpy pandas glob
```
Alternatively, you can use the available cfg/environment.yml file with the complete conda environment. Read instructions [here](https://conda.io/projects/conda/en/latest/user-guide/tasks/manage-environments.html#creating-an-environment-from-an-environment-yml-file) on how to use it.
## Usage
To run the full project you can use run.sh file. Set correct directory and activate conda environment first.

## Project Structure
The project folder contains the following files and directories:

- README.md: The project README file, which provides an overview of the project.
- main.py: The main script file, which contains the main() function that runs the project.
- src: A directory that contains utility functions used in the project.
- data: A directory that contains the raw and parsed data used in the project.
- raw: A directory that contains the raw data files.
- parsed: A directory that contains the parsed data files.
- res: A directory that contains the output measurements report file.
- cfg: A directory that contains the configuration files.
- run.sh A shell script that runs the project.

## Acknowledgments
This project was created for research purposes only created at IMCF Biocev.