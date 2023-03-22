# BC EV Chraging Stations
The current state of the public electric vehicle (EV) charging station network in British Columbia (B.C.).
The notebook containing the detailed analysis is provided [analysis notebook ](notebook/01-analysis.ipynb).


![ev-staion-growth](./reports/yearly-station-growth.png?raw=true)

## Reproducing the Notebook
Follow these instruction to reproduce the analysis in the notebook:

1. make sure you have anaconda installed
2. open the anaconda prompt and run the following commands
```
conda env create -f environment.yml
```
4. run the command below which opens a browser tab
```
jupyter lab
```
5. navigate to the project folder and then to the notebook file
6. the notebook should now run successfully

## Project Organization

-------------------------
```
.
├── README.md
├── data
│   └── raw
│       └── raw_data.csv
├── environment.yml
├── notebook
│   └── 01-analysis.ipynb
├── reports
│   ├── Number-of-Level-2-and-DC-FC-stations.png
│   ├── all-stations.html
│   ├── count of connection types.png
│   ├── distribution of ports count.png
│   ├── planned-stations-only.html
│   ├── pricing-info.png
│   ├── staions-with-free-charging.html
│   ├── station-with-maximum-number-of-ports.html
│   ├── stations-with-fast-charging-capability.html
│   └── yearly-station-growth.png
└── src
    ├── __init__.py
    ├── __pycache__
    │   ├── processing.cpython-39.pyc
    │   └── visualization.cpython-39.pyc
    ├── processing.py
    └── visualization.py

        
```