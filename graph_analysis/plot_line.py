import argparse
import json
import matplotlib.pyplot as plt
import operator

if __name__ == "__main__":
    # Set up argument parser to accept the file path from the command line.
    # This makes the script reusable for different data files.
    parser = argparse.ArgumentParser(description="Plot a line graph from a JSON file with key-value pairs.")
    parser.add_argument("--path", type=str, required=True, help="Path to the JSON file.")
    args = parser.parse_args()
    
    # Open and load the JSON data from the specified file.
    try:
        with open(args.path, "r") as f:
            dictionary = json.load(f)
    except FileNotFoundError:
        print(f"Error: The file at {args.path} was not found.")
        exit()
    except json.JSONDecodeError:
        print(f"Error: The file at {args.path} is not a valid JSON file.")
        exit()
    
    # The keys in the JSON are strings representing floating-point numbers.
    # We need to convert them to actual floats for plotting.
    # The values are the corresponding cumulative frequencies.
    
    # To ensure the line plot is drawn correctly, we must sort the data
    # by the centrality value (the key).
    
    # Convert dictionary items to a list of tuples and sort by the key (item[0])
    # after converting the key to a float.
    sorted_items = sorted(dictionary.items(), key=lambda item: float(item[0]))
    
    # Unpack the sorted tuples into separate lists for keys and values.
    keys = [float(item[0]) for item in sorted_items]
    values = [item[1] for item in sorted_items]
    
    # --- Plotting the Data ---
    plt.figure(figsize=(10, 6)) # Create a figure with a specific size for better readability.
    
    # Use plt.plot() for a line graph.
    # 'keys' are the x-coordinates (centrality).
    # 'values' are the y-coordinates (cumulative frequency).
    plt.plot(keys, values, marker='.', linestyle='-')
    
    # Add labels to the axes and a title to the plot for clarity.
    # Increased fontsize for better visibility.
    plt.xlabel('Centrality', fontsize=14)
    plt.ylabel('Cumulative Frequency', fontsize=14)

    
    # Increase the font size of the tick labels on both axes
    plt.tick_params(axis='both', which='major', labelsize=12)
    
    # Add a grid for easier reading of values.
    plt.grid(True)
    
    # Display the plot.
    plt.show()

