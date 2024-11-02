import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.stats import ttest_ind
import numpy as np

# Load data
axon_data = pd.read_csv('res/measurements.csv')

# Simplify column names
axon_data.columns = [
    'Genotype', 'Sample', 'NameOfMeasurement', 'Time', 'CoordinateOfTip', 
    'Axon_length_um', 'Speed_um_per_sec', 'Growth_distance_um', 'Angle change (deg)',
    'Total growth (um)', 'Total_speed_um_per_sec', 'Total angle change (deg)'
]

# Exclude speed variables and filter out columns with NaN values
filtered_data = axon_data.drop(columns=['Speed_um_per_sec', 'Total_speed_um_per_sec', 'Axon_length_um', 'Growth_distance_um', 'NameOfMeasurement', 'CoordinateOfTip'])
filtered_data = filtered_data[(filtered_data['Time'] != 0)]

# Variables to analyze after filtering
variables = [col for col in filtered_data.columns if col not in ['Genotype', 'Sample', 'NameOfMeasurement', 'Time', 'CoordinateOfTip']]

# Initialize plot dimensions
fig, axes = plt.subplots(1, len(variables), figsize=(4 * len(variables), 8))
results = {}

# Create boxplots and t-tests
for i, var in enumerate(variables):
    sns.boxplot(x='Genotype', y=var, data=filtered_data, ax=axes[i], flierprops={'marker': '.', 'markersize': 3}, boxprops={'facecolor':'None'}, whiskerprops={'linewidth': 0.5}, capprops={'linewidth': 0.5})
    sns.swarmplot(x='Genotype', y=var, data=filtered_data, hue='Sample', ax=axes[i], alpha=0.5, size=3, linewidth=0.5, legend=False)
    
    # Average (group) data from each sample
    grouped_data = filtered_data.groupby(['Genotype', 'Sample'])[var].mean().reset_index()

    # Signify the mean of each sample
    sns.swarmplot(x='Genotype', y=var, data=grouped_data, hue='Sample', ax=axes[i], alpha=1, size=6, linewidth=0.5, legend=(i == len(variables) - 1))
    axes[i].legend()
    axes[i].set_title(f'{var}')
    axes[i].set_xlabel("Genotype")
    axes[i].set_ylabel("")
    
    # Remove top and right spines
    axes[i].spines['top'].set_visible(False)
    axes[i].spines['right'].set_visible(False)
    
    # Run t-test
    control_vals = filtered_data[(filtered_data['Genotype'] == 'Control')][var]
    mutant_vals = filtered_data[(filtered_data['Genotype'] == 'IsI1CKO')][var]
    
    # Remove NaN from the list
    control_vals = control_vals[~np.isnan(control_vals)]
    mutant_vals = mutant_vals[~np.isnan(mutant_vals)]

    if len(control_vals) > 0 and len(mutant_vals) > 0:
        t_stat, p_val = ttest_ind(control_vals, mutant_vals, equal_var=False)
        results[var] = {"t-statistic": t_stat, "p-value": p_val}
        if p_val < 0.001:
            p_str = "<0.001"
        else:
            p_str = f"{p_val:.3f}"
        axes[i].text(0.5, 0.95, f"p-value: {p_str}", transform=axes[i].transAxes, ha='center')
        axes[i].text(0.5, 0.9, f"n: {len(control_vals) + len(mutant_vals)}", transform=axes[i].transAxes, ha='center')
    else:
        results[var] = {"t-statistic": None, "p-value": None}

plt.tight_layout()
plt.show()

# Print results
print(results)

