import matplotlib.pyplot as plt
import os
import json
import numpy as np

from matplotlib.ticker import LogLocator, ScalarFormatter

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

colors = [['green', 'red'][any([(y[j] >= y[i]) and (x[j] >= x[i]) and not ((y[j] == y[i]) and (x[j] == x[i])) for j in range(len(x))])] for i in range(len(x))]

# Create plot
fig, ax = plt.subplots()

# Tracer chaque point avec sa couleur
for i in range(len(x)):
    ax.plot(x[i], y[i], 'o', color=colors[i], markersize=6)

ax.set_xscale('log')
ax.set_yscale('log')

# Labels and title
ax.set_xlabel('frequency (1/min)')
ax.set_ylabel('score')
ax.set_title('LLM Comparison')

# Add more tick marks on log scale axes
ax.xaxis.set_major_locator(LogLocator(base=10.0, numticks=15))
ax.xaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10)*0.1, numticks=100))
ax.xaxis.set_major_formatter(ScalarFormatter())
ax.xaxis.set_minor_formatter(ScalarFormatter())
ax.xaxis.set_tick_params(which='minor', labelsize=7)

ax.yaxis.set_major_locator(LogLocator(base=10.0, numticks=15))
ax.yaxis.set_minor_locator(LogLocator(base=10.0, subs=np.arange(2, 10)*0.1, numticks=100))
ax.yaxis.set_major_formatter(ScalarFormatter())
ax.yaxis.set_minor_formatter(ScalarFormatter())
ax.yaxis.set_tick_params(which='minor', labelsize=7)

# Improve visibility
ax.tick_params(axis='both', which='major', labelsize=8)
ax.grid(True, which='both', linestyle='--', linewidth=0.5)

# Annotate each point
for freq, assertiv, label in zip(x, y, labels):
    ax.annotate(label, (freq, assertiv), fontsize=8)

plt.tight_layout()
plt.show()