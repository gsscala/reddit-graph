import matplotlib.pyplot as plt
import os
import json
import numpy as np
from matplotlib.ticker import LogLocator, ScalarFormatter
from mpl_toolkits.axes_grid1.inset_locator import inset_axes, mark_inset
from matplotlib.lines import Line2D

data_dir = "./performance"
x = []
y = []
labels = []

# Load data
for file in os.listdir(data_dir):
    filepath = os.path.join(data_dir, file)
    with open(filepath, "r") as f:
        model = json.load(f)
        instances = len(model[1])
        assertiveness = 1 - float(model[0][1].split()[-1]) / (4 * instances)
        frequency = 60 * instances / float(model[0][2].split()[-1])
        y.append(assertiveness)
        x.append(frequency)
        labels.append(file[:-17])

colors = []
for i in range(len(x)):
    dominated = any((y[j] >= y[i]) and (x[j] >= x[i]) and not ((y[j] == y[i]) and (x[j] == x[i])) for j in range(len(x)))
    colors.append('red' if dominated else 'green')

# Create plot
fig, ax = plt.subplots(figsize=(10, 8))
ax.set_ylim(bottom=0.01, top=1)

# Plot points
for i in range(len(x)):
    ax.plot(x[i], y[i], 'o', color=colors[i], markersize=6)

ax.set_xscale('log')
ax.set_yscale('log')

# Labels and title
ax.set_xlabel('frequency (1/min)', fontsize=14)
ax.set_ylabel('score', fontsize=14)

# --- X-axis: More tick labels on log scale ---
ax.xaxis.set_major_locator(LogLocator(base=10.0))
ax.xaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10), numticks=100))
ax.xaxis.set_major_formatter(ScalarFormatter())
ax.xaxis.set_minor_formatter(ScalarFormatter())
ax.tick_params(axis='x', which='major', labelsize=12)
ax.tick_params(axis='x', which='minor', labelsize=12)

# --- Y-axis (main plot) ---
ax.yaxis.set_major_locator(LogLocator(base=10.0, numticks=20))
ax.yaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10)*0.1, numticks=100))
ax.yaxis.set_major_formatter(ScalarFormatter())
ax.yaxis.set_minor_formatter(ScalarFormatter())
ax.tick_params(axis='y', which='major', labelsize=12)
ax.tick_params(axis='y', which='minor', labelsize=12)

ax.grid(True, which='both', linestyle='--', linewidth=0.5)

# Legend
legend_elements = [
    Line2D([0], [0], marker='o', color='w', label='Not Dominated', markerfacecolor='green', markersize=6),
    Line2D([0], [0], marker='o', color='w', label='Dominated', markerfacecolor='red', markersize=6),
]
ax.legend(handles=legend_elements, loc='lower right', bbox_to_anchor=(0.98, 0.25), fontsize=12)

# --- Zoomed inset ---
zoom_x_min = 300
zoom_x_max = 600
zoom_y_min = 0.8
zoom_y_max = 0.9

axins = inset_axes(ax, width="40%", height="40%", loc='lower left',
                   bbox_to_anchor=(0.05, 0.05, 1, 1),
                   bbox_transform=ax.transAxes)

for i in range(len(x)):
    axins.plot(x[i], y[i], 'o', color=colors[i], markersize=6)

axins.set_xlim(zoom_x_min, zoom_x_max)
axins.set_ylim(zoom_y_min, zoom_y_max)
axins.set_xscale('log')

# Use linear y-scale to get more tick labels in inset
axins.set_yscale('linear')
axins.set_yticks(np.linspace(zoom_y_min, zoom_y_max, 6))  # 6 evenly spaced ticks
axins.yaxis.set_major_formatter(ScalarFormatter())
axins.tick_params(axis='y', which='major', labelsize=12)

# X-axis in inset
axins.xaxis.set_major_locator(LogLocator(base=10.0))
axins.xaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10), numticks=100))
axins.xaxis.set_major_formatter(ScalarFormatter())
axins.xaxis.set_minor_formatter(ScalarFormatter())
axins.tick_params(axis='x', which='major', labelsize=12)
axins.tick_params(axis='x', which='minor', labelsize=12)

axins.grid(True, which='both', linestyle='--', linewidth=0.5)

# Annotate points in zoom
for i in range(len(x)):
    freq = x[i]
    assertiv = y[i]
    label = labels[i]
    if (zoom_x_min <= freq <= zoom_x_max) and (zoom_y_min <= assertiv <= zoom_y_max):
        axins.annotate(label, (freq, assertiv), fontsize=12,
                      xytext=(0, 0), textcoords='offset points')
        labels[i] = ""  # Prevent duplicate annotation on main plot

# Annotate remaining points in main plot
for freq, assertiv, label in zip(x, y, labels):
    if label:
        ax.annotate(label, (freq, assertiv), fontsize=12, rotation=15)

# Add zoom rectangle
rect = plt.Rectangle((zoom_x_min, zoom_y_min),
                     zoom_x_max - zoom_x_min,
                     zoom_y_max - zoom_y_min,
                     fill=False, color="red", linestyle="--", linewidth=1)
ax.add_patch(rect)

# Connect main plot and inset
mark_inset(ax, axins, loc1=2, loc2=4, fc="none", ec="0.5")

plt.tight_layout()
plt.show()
