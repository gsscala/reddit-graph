import numpy as np
import matplotlib.pyplot as plt
import json
import math

# Load the data from the JSON file
with open("centrality.json", "r") as f:
    data_dict = json.load(f)

# Extract keys (degree centrality) and values (frequency)
x_raw = list(map(float, data_dict.keys()))  # Convert keys to float
y_raw = list(map(float, data_dict.values()))  # Convert values to float

# Filter out zero values (log(0) undefined)
x_clean = []
y_clean = []
for x_val, y_val in zip(x_raw, y_raw):
    if x_val > 0 and y_val > 0:
        x_clean.append(x_val)
        y_clean.append(y_val)

# Transform data to log-space for linear regression
log_x = np.log(x_clean)
log_y = np.log(y_clean)

# Perform linear regression in log-space
A = np.vstack([log_x, np.ones(len(log_x))]).T
slope, log_intercept = np.linalg.lstsq(A, log_y, rcond=None)[0]

# Calculate parameters of the power law: y = a * x^(-gamma)
gamma = -slope
a = np.exp(log_intercept)

# Compute predicted values and R² in log-space
predicted_log_y = slope * log_x + log_intercept
ss_res = np.sum((log_y - predicted_log_y) ** 2)
ss_tot = np.sum((log_y - np.mean(log_y)) ** 2)
r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else 0

# Generate points for the fitted curve
x_fit = np.logspace(np.log10(min(x_clean)), np.log10(max(x_clean)), 500)
y_fit = a * (x_fit ** (-gamma))

# Plot the data and the fitted power law
plt.figure(figsize=(10, 6))
plt.scatter(x_clean, y_clean, alpha=0.6, label='Data', color='blue')
plt.plot(x_fit, y_fit, 'r-', linewidth=2, label=f'Fit: $y = {a:.8f} \\cdot x^{{-{gamma:.3f}}}$')

# Configure plot with larger text sizes
plt.xscale('log')
plt.yscale('log')
plt.xlabel('Degree Centrality (log scale)', fontsize=14)  # Increased fontsize
plt.ylabel('Frequency (log scale)', fontsize=14)  # Increased fontsize
plt.legend(fontsize=12)  # Increased legend fontsize

# Increase the size of the tick labels
plt.xticks(fontsize=12)
plt.yticks(fontsize=12)

plt.grid(True, which="both", ls="-", alpha=0.3)
plt.tight_layout()
plt.show()
