# Katharina Optical Profiler

Tools for processing, visualizing, and analysing surface height measurements acquired with a Keyence VK-X3000 optical profiler.

The following code is largely based on these GitHub repositories: 
* https://github.com/duserzym/Keyence_VKX3000_data_processing 
* https://github.com/torkian/vk4-python-driver/tree/master

Note: Not all of the functions included in 'scripts/' are necessary for stitching, but may be useful for other image processing purposes.


## Repository Structure

* `raw_data_vk/` – raw optical profiler measurement files (stored on the BW server)
* `processed_data_csv/` – processed data and example CSV files
* `notebooks/` – Jupyter notebooks for analysis and visualization
* `scripts/` – reusable Python scripts and functions
* `README.md` – project documentation
* `.gitignore` – Git configuration for excluding large data files


## Data Storage

Raw measurement files and processed datasets are stored on the BW server and are not included in this repository. Links to the datasets are provided below:

* Raw data: https://bwsyncandshare.kit.edu/s/n7kFdPBs8ZHDSMW?dir=/Optical%20profiler%20Katharina/Raw%20data%20vk
* Processed data: https://bwsyncandshare.kit.edu/s/n7kFdPBs8ZHDSMW?dir=/Optical%20profiler%20Katharina/Processed%20data%20csv
