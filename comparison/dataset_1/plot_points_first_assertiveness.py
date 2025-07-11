import matplotlib.pyplot as plt
import os
import json
import numpy as np
from matplotlib.ticker import LogLocator, ScalarFormatter, FuncFormatter
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
        assertiveness = float(model[0][0].split()[-1]) / instances
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
    ax.plot(x[i], y[i], 'o', color=colors[i], markersize=10)

ax.set_xscale('log')  # Keep x-axis log
# Removed y-axis log scale: ax.set_yscale('log')

# Labels and title
ax.set_xlabel('frequency (1/min)', fontsize=25)
ax.set_ylabel('assertiveness', fontsize=25)

# X-axis: log scale with plain number formatting
ax.xaxis.set_major_locator(LogLocator(base=10.0, subs='auto', numticks=20))
ax.xaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10) * 0.1, numticks=100))
x_formatter = ScalarFormatter()
x_formatter.set_scientific(False)
ax.xaxis.set_major_formatter(FuncFormatter(lambda val, pos: f'{val:g}'))
ax.xaxis.set_minor_formatter(plt.NullFormatter())

# Y-axis: linear scale with plain formatting
ax.yaxis.set_major_formatter(ScalarFormatter())
ax.tick_params(axis='y', which='both', labelsize=20)
ax.grid(True, which='both', axis='y', linestyle='--', linewidth=0.5)

# Improve visibility
ax.tick_params(axis='x', which='both', labelsize=20, rotation=60)
ax.grid(True, which='both', axis='x', linestyle='--', linewidth=0.5)

# Reference line
sota_value = 0.6227
ax.axhline(y=sota_value, color='blue', linestyle='--', linewidth=1.5, label='SOTA')

# Legend
legend_elements = [
    Line2D([0], [0], marker='o', color='w', label='Not Dominated', markerfacecolor='green', markersize=14),
    Line2D([0], [0], marker='o', color='w', label='Dominated', markerfacecolor='red', markersize=14),
    Line2D([0], [0], color='blue', linestyle='--', linewidth=3, label='SOTA performance')
]
ax.legend(handles=legend_elements,
          loc='upper right',
          fontsize=20)

# Zoomed inset
zoom_x_min = 300
zoom_x_max = 600
zoom_y_min = 0.42
zoom_y_max = 0.55

axins = inset_axes(ax, width="40%", height="40%", loc='lower left',
                   bbox_to_anchor=(0.05, 0.05, 1, 1),
                   bbox_transform=ax.transAxes)

for i in range(len(x)):
    axins.plot(x[i], y[i], 'o', color=colors[i], markersize=10)

axins.set_xlim(zoom_x_min, zoom_x_max)
axins.set_ylim(zoom_y_min, zoom_y_max)
axins.set_xscale('log')  # Keep log scale on x-axis
# Removed log scale on y-axis: axins.set_yscale('log')

axins.grid(True, which='major', axis='both', linestyle='--', linewidth=0.5)

# Format zoomed-in axes
xins_formatter = ScalarFormatter()
xins_formatter.set_scientific(False)
axins.xaxis.set_major_formatter(FuncFormatter(lambda val, pos: f'{val:g}'))
axins.xaxis.set_minor_formatter(plt.NullFormatter())

yins_formatter = ScalarFormatter()
yins_formatter.set_scientific(False)
axins.yaxis.set_major_formatter(FuncFormatter(lambda val, pos: f'{val:g}'))
axins.yaxis.set_minor_formatter(plt.NullFormatter())

axins.xaxis.set_major_locator(LogLocator(base=10.0, subs='auto', numticks=15))
axins.xaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10) * 0.1, numticks=100))

# Annotate points in zoomed section
for i in range(len(x)):
    freq = x[i]
    assertiv = y[i]
    label = labels[i]
    if (zoom_x_min <= freq <= zoom_x_max) and (zoom_y_min <= assertiv <= zoom_y_max):
        axins.annotate(label, (freq, assertiv), fontsize=20,
                       xytext=(3, 2), textcoords='offset points')
        labels[i] = ""

# Annotate remaining points in main plot
for freq, assertiv, label in zip(x, y, labels):
    ax.annotate(label, (freq, assertiv), fontsize=20, rotation=30)

# Add zoom rectangle
rect = plt.Rectangle((zoom_x_min, zoom_y_min),
                     zoom_x_max - zoom_x_min,
                     zoom_y_max - zoom_y_min,
                     fill=False, color="red", linestyle="--", linewidth=1)
ax.add_patch(rect)

mark_inset(ax, axins, loc1=2, loc2=4, fc="none", ec="0.5")
axins.tick_params(axis='both', which='both', labelsize=20)

plt.tight_layout()
plt.show()
