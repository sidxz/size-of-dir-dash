import os
import sys
import urllib.parse
import subprocess
import random
import math

# Function to calculate the size of a directory using du -sh command
def get_directory_size(directory):
    try:
        result = subprocess.run(['du', '-sh', directory], capture_output=True, text=True)
        output = result.stdout.strip()
        size_str = output.split()[0]
        size, unit = float(size_str[:-1]), size_str[-1]
        units = {'K': 1024, 'M': 1024**2, 'G': 1024**3, 'T': 1024**4}
        size_bytes = size * units[unit]
        return size_bytes
    except subprocess.CalledProcessError:
        return 0

# Function to format the size in human-readable format
def format_size(size):
    if size == 0:
        return "0 B"
    units = ["B", "KB", "MB", "GB", "TB"]
    i = int(math.floor(math.log(size, 1024)))
    i = min(i, len(units) - 1)  # Ensure the index doesn't exceed the number of units
    size = round(size / (1024 ** i), 2)
    return f"{size} {units[i]}"

# Function to generate HTML for directory entries
def generate_directory_entry_html(name, size):
    return f'<tr><td>{name}</td><td>{format_size(size)}</td></tr>'

# Function to generate the HTML file
def generate_html_file(directory, depth, output_file):
    try:
        with open(output_file, 'w') as f:
            f.write('<html><head><style>')
            # Add your custom CSS styles here
            f.write('table {width: 100%; border-collapse: collapse; font-family: Arial, sans-serif;}')
            f.write('th, td {padding: 8px; text-align: left; border-bottom: 1px solid #ddd;}')
            f.write('tbody tr:hover {background-color: #f5f5f5;}')
            f.write('</style>')

            # Include the required JavaScript libraries
            f.write('<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>')

            f.write('</head><body>')
            f.write('<table><thead><tr><th>Directory</th><th>Size</th></tr></thead><tbody>')

            # Traverse the directory
            stack = [(directory, 0)]
            directory_sizes = {}
            while stack:
                current_dir, current_depth = stack.pop()
                size = get_directory_size(current_dir)
                directory_sizes[current_dir] = size

                # Generate HTML entry for the current directory
                encoded_dir = urllib.parse.quote(current_dir)  # Encode directory name for URLs
                html_entry = generate_directory_entry_html(encoded_dir, size)
                f.write(html_entry)

                if current_depth < depth:
                    # Add subdirectories to the stack
                    for entry in os.scandir(current_dir):
                        if entry.is_dir() and not entry.is_symlink():
                            try:
                                stack.append((entry.path, current_depth + 1))
                            except PermissionError:
                                pass

            f.write('</tbody></table>')

            # Generate pie chart visualization
            f.write('<div id="chart"></div>')
            f.write('<script>')
            f.write('var sizes = {')
            for i, (dir_path, size) in enumerate(directory_sizes.items()):
                f.write(f'"{dir_path}": {size}')
                if i < len(directory_sizes) - 1:
                    f.write(', ')
            f.write('};')

            f.write('var data = [{')
            f.write('values: Object.values(sizes),')
            f.write('labels: Object.keys(sizes),')
            f.write("type: 'pie',")
            f.write('marker: {')
            f.write('colors: [')
            for _ in range(len(directory_sizes)):
                f.write(f'"#{random.randint(0, 0xFFFFFF):06x}",')
            f.write(']')
            f.write('}')
            f.write('}];')

            f.write('var layout = {')
            f.write('height: 400,')
            f.write('width: 500')
            f.write('};')

            f.write('Plotly.newPlot("chart", data, layout);')
            f.write('</script>')

            f.write('</body></html>')

    except IOError:
        print(f"Failed to create HTML file: {output_file}")

# Main function
def main():
    if len(sys.argv) < 4:
        print("Usage: python dashboard.py <directory> <depth> <output_file>")
        return

    directory = sys.argv[1]
    depth = int(sys.argv[2])
    output_file = sys.argv[3]

    generate_html_file(directory, depth, output_file)

    # Open the generated HTML file in the default web browser
    try:
        subprocess.run(['open', output_file], check=True)
    except subprocess.SubprocessError:
        print(f"Failed to open HTML file: {output_file}")

if __name__ == '__main__':
    main()
