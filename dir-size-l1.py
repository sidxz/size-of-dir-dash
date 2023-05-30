import argparse
import os
from tqdm import tqdm
import matplotlib.pyplot as plt

# Function to calculate the total size of a directory
def calculate_directory_size(directory):
    total_size = 0

    for root, dirs, files in os.walk(directory, followlinks=False):
        for file in files:
            file_path = os.path.join(root, file)
            try:
                total_size += os.path.getsize(file_path)
            except OSError as e:
                print(f"Error accessing file: {file_path}. Error: {str(e)}")
            except Exception as e:
                print(f"Error processing file: {file_path}. Error: {str(e)}")

    return total_size

# Function to get folder sizes
def get_folder_sizes(directory):
    folder_sizes = {}
    total_size = calculate_directory_size(directory)

    with tqdm(total=total_size, unit='B', unit_scale=True, desc="Calculating folder sizes") as pbar:
        for root, dirs, files in os.walk(directory, followlinks=False):
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)

                    folder_path = os.path.dirname(file_path)
                    if folder_path not in folder_sizes:
                        folder_sizes[folder_path] = 0
                    folder_sizes[folder_path] += file_size

                    pbar.update(file_size)
                except OSError as e:
                    print(f"Error accessing file: {file_path}. Error: {str(e)}")
                except Exception as e:
                    print(f"Error processing file: {file_path}. Error: {str(e)}")

    return folder_sizes, total_size

# Function to generate HTML report with chart
def generate_html_report(folder_sizes, total_size, chart_file):
    # Generate the HTML report based on folder sizes and total size
    report = f"""
    <html>
    <head>
        <title>Folder Sizes Report</title>
        <style>
            table, th, td {{
                border: 1px solid black;
                border-collapse: collapse;
                padding: 5px;
                text-align: left;
            }}
        </style>
        <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    </head>
    <body>
        <h1>Folder Sizes Report</h1>
        <div id="chart"></div>
        <table>
            <tr>
                <th>Folder</th>
                <th>Size (Bytes)</th>
                <th>Size (Human Readable)</th>
            </tr>
    """

    chart_data = []
    chart_labels = []
    for folder, size in sorted(folder_sizes.items(), key=lambda x: x[1], reverse=True):
        size_human_readable = sizeof_fmt(size)
        report += f"""
            <tr>
                <td>{folder}</td>
                <td>{size}</td>
                <td>{size_human_readable}</td>
            </tr>
        """
        chart_data.append(size)
        chart_labels.append(folder)

    total_size_human_readable = sizeof_fmt(total_size)
    report += f"""
            <tr>
                <td><strong>Total Size</strong></td>
                <td><strong>{total_size}</strong></td>
                <td><strong>{total_size_human_readable}</strong></td>
            </tr>
        </table>
        <script>
            var data = [{{
                values: {chart_data},
                labels: {chart_labels},
                type: 'pie'
            }}];
            
            var layout = {{
                title: 'Folder Size Distribution'
            }};
            
            Plotly.newPlot('chart', data, layout);
        </script>
    </body>
    </html>
    """

    return report

# Function to save the report to a file
def save_report(report, output_file):
    with open(output_file, 'w') as f:
        f.write(report)

# Helper function to format file sizes in human-readable format
def sizeof_fmt(num, suffix='B'):
    for unit in ['','Ki','Mi','Gi','Ti','Pi','Ei','Zi']:
        if abs(num) < 1024.0:
            return f"{num:.2f} {unit}{suffix}"
        num /= 1024.0
    return f"{num:.2f} Yi{suffix}"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate folder sizes report')
    parser.add_argument('directory', help='Directory path')
    parser.add_argument('output_file', help='Output file path')
    args = parser.parse_args()

    if not os.path.isdir(args.directory):
        print("Error: The specified directory does not exist.")
        exit(1)

    folder_sizes, total_size = get_folder_sizes(args.directory)
    report = generate_html_report(folder_sizes, total_size)

    save_report(report, args.output_file)
    print(f"Report generated and saved to {args.output_file}.")
