import argparse
import os
from datetime import datetime
from tqdm import tqdm


def get_folder_sizes(directory):
    folder_sizes = []
    num_folders = 0
    for entry in os.scandir(directory):
        if entry.is_dir() and not entry.is_symlink():
            num_folders += 1

    with tqdm(total=num_folders, desc="Calculating folder sizes") as pbar:
        for entry in os.scandir(directory):
            if entry.is_dir() and not entry.is_symlink():
                total_size = 0
                last_accessed_time = os.path.getatime(entry.path)
                for root, dirs, files in os.walk(entry.path, followlinks=False):
                    for file in files:
                        file_path = os.path.join(root, file)
                        file_path = f'"{file_path}"'  # Wrap file path with double quotes
                        total_size += os.stat(file_path).st_size
                        file_last_accessed_time = os.path.getatime(file_path)
                        if file_last_accessed_time > last_accessed_time:
                            last_accessed_time = file_last_accessed_time
                folder_sizes.append((entry.path, total_size, last_accessed_time))
                folder_sizes.extend(get_folder_sizes(entry.path))  # Recursively process subdirectories
                pbar.update(1)

    return folder_sizes


def consolidate_folder_sizes(folder_sizes):
    consolidated_sizes = {}
    consolidated_last_accessed_times = {}
    for folder, size, last_accessed_time in folder_sizes:
        folder_name = os.path.basename(folder)
        if folder_name not in consolidated_sizes:
            consolidated_sizes[folder_name] = size
            consolidated_last_accessed_times[folder_name] = last_accessed_time
        else:
            consolidated_sizes[folder_name] += size
            if last_accessed_time > consolidated_last_accessed_times[folder_name]:
                consolidated_last_accessed_times[folder_name] = last_accessed_time
    return consolidated_sizes, consolidated_last_accessed_times


def convert_timestamp(timestamp):
    access_time = datetime.fromtimestamp(timestamp)
    return access_time.strftime('%Y-%m-%d %H:%M:%S')


def generate_html_report(folder_sizes, consolidated_sizes, consolidated_last_accessed_times):
    report = """
    <html>
        <head>
            <title>Folder Sizes Report</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                }
                h1 {
                    color: #333333;
                }
                table {
                    border-collapse: collapse;
                    width: 100%;
                }
                th, td {
                    padding: 8px;
                    text-align: left;
                    border-bottom: 1px solid #dddddd;
                }
                th {
                    background-color: #f2f2f2;
                }
                .sortable {
                    cursor: pointer;
                }
                .chart-container {
                    width: 600px;
                    margin: 20px auto;
                    text-align: center;
                }
            </style>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <script>
                function sortTable(columnIndex) {
                    var table, rows, switching, i, x, y, shouldSwitch;
                    table = document.getElementById("reportTable");
                    switching = true;
                    while (switching) {
                        switching = false;
                        rows = table.rows;
                        for (i = 1; i < (rows.length - 1); i++) {
                            shouldSwitch = false;
                            x = rows[i].getElementsByTagName("TD")[columnIndex];
                            y = rows[i + 1].getElementsByTagName("TD")[columnIndex];
                            if (isNaN(x.innerHTML)) {
                                if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {
                                    shouldSwitch = true;
                                    break;
                                }
                            } else {
                                if (parseFloat(x.innerHTML) < parseFloat(y.innerHTML)) {
                                    shouldSwitch = true;
                                    break;
                                }
                            }
                        }
                        if (shouldSwitch) {
                            rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
                            switching = true;
                        }
                    }
                }
            </script>
        </head>
        <body>
            <h1>Folder Sizes Report</h1>
            <h2>Individual Folder Sizes</h2>
            <table id="reportTable">
                <tr>
                    <th class="sortable" onclick="sortTable(0)">Folder</th>
                    <th class="sortable" onclick="sortTable(1)">Size (terabytes)</th>
                    <th class="sortable" onclick="sortTable(2)">Last Accessed Time</th>
                </tr>
    """

    for folder, size, last_accessed_time in folder_sizes:
        size_in_tb = size / (1024 ** 4)  # Convert to terabytes
        access_time = convert_timestamp(last_accessed_time)
        report += f"""
                <tr>
                    <td>{folder}</td>
                    <td>{size_in_tb:.2f} TB</td>
                    <td>{access_time}</td>
                </tr>
        """

    report += """
            </table>

            <h2>Consolidated Folder Sizes</h2>
            <table id="reportTable">
                <tr>
                    <th class="sortable" onclick="sortTable(0)">Folder</th>
                    <th class="sortable" onclick="sortTable(1)">Size (terabytes)</th>
                    <th class="sortable" onclick="sortTable(2)">Last Accessed Time</th>
                </tr>
    """

    for folder, size in consolidated_sizes.items():
        size_in_tb = size / (1024 ** 4)  # Convert to terabytes
        access_time = convert_timestamp(consolidated_last_accessed_times[folder])
        report += f"""
                <tr>
                    <td>{folder}</td>
                    <td>{size_in_tb:.2f} TB</td>
                    <td>{access_time}</td>
                </tr>
        """

    report += """
            </table>

            <div class="chart-container">
                <canvas id="chart"></canvas>
            </div>

            <script>
                var ctx = document.getElementById('chart').getContext('2d');
                var chart = new Chart(ctx, {
                    type: 'pie',
                    data: {
                        labels: ['"""+ "', '".join([os.path.basename(folder) for folder, _, _ in folder_sizes])+ """'],
                        datasets: [{
                            label: 'Top-level Directory Sizes',
                            data: ["""+ ", ".join([str(size) for _, size, _ in folder_sizes])+ """],
                            backgroundColor: [
                                '#FF6384',
                                '#36A2EB',
                                '#FFCE56',
                                '#8bc34a',
                                '#e91e63',
                                '#00bcd4',
                                '#f44336',
                                '#9c27b0',
                                '#673ab7',
                                '#ff5722',
                                '#795548',
                                '#607d8b',
                                '#03a9f4',
                                '#ff9800',
                                '#009688',
                                '#ffeb3b',
                                '#9e9e9e',
                                '#ff00ff',
                                '#0000ff',
                                '#00ff00'
                            ]
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false
                    }
                });
            </script>

        </body>
    </html>
    """
    return report


def save_report(report, output_file):
    with open(output_file, 'w') as f:
        f.write(report)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Generate folder sizes report')
    parser.add_argument('directory', help='Directory path')
    parser.add_argument('output_file', help='Output file path')
    args = parser.parse_args()

    folder_sizes = get_folder_sizes(args.directory)
    consolidated_sizes, consolidated_last_accessed_times = consolidate_folder_sizes(folder_sizes)

    report = generate_html_report(folder_sizes, consolidated_sizes, consolidated_last_accessed_times)

    save_report(report, args.output_file)
    print(f"Report generated and saved to {args.output_file}.")
