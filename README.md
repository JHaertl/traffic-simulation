# traffic-simulation

Agent-based, space continuous, time discrete traffic simulation.  
Driver decisions based on [IDM][1] and [MOBIL][2] models.  
Sample generation tool for deep learning applications.

## Getting Started

The [config](config.ini) file is used to configure the simulation environment.  
Check the [documentation](doc/documentation.md) for a detailed guide on how to work with this simulation.

### Requirements

Python 3.x  
Numpy and OpenCV (only for rendering)

### Running the simulation

Simply execute run_simulation.py
```
python run_simulation.py
```
## Author

**Jonathan Härtl**

[1]:https://arxiv.org/abs/cond-mat/0002177
[2]:http://www.mtreiber.de/publications/MOBIL_TRB.pdf
